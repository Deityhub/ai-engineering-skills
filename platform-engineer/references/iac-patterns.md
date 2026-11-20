# Infrastructure as Code Patterns

## Terraform Best Practices

### Module Structure
```
modules/
├── vpc/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── versions.tf
│   ├── README.md
│   └── test/
│       ├── main.tf
│       └── outputs.tf
├── eks/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── ...
└── rds/
    └── ...
```

### Module Standards
- **`versions.tf`**: Pin provider versions (`required_version`, `required_providers`)
- **`variables.tf`**: All inputs with `type`, `description`, `validation` blocks, `default` only for safe values
- **`outputs.tf`**: All meaningful outputs with `description`, `sensitive = true` for secrets
- **`README.md`**: Auto-generated with `terraform-docs` — usage, inputs, outputs, examples
- **Tests**: Terratest (Go) or kitchen-terraform for integration tests

### State Management
```hcl
# backend "s3" for AWS
terraform {
  backend "s3" {
    bucket         = "tf-state-prod"
    key            = "infra/eks/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "tf-state-locks"
  }
}
```
- **Remote backend only** — S3+DynamoDB (AWS), GCS (GCP), Azure Blob (Azure)
- **State locking** — DynamoDB, GCS object locking, Azure Blob leases
- **Separate state per environment** — Never share state across envs
- **Drift detection** — Scheduled `terraform plan -refresh-only` → alert on changes

### Workspaces & Environments
```hcl
# Environment-specific configuration via workspace
locals {
  env_config = {
    dev  = { instance_size = "t3.medium", min_nodes = 1, max_nodes = 3 }
    staging = { instance_size = "t3.large", min_nodes = 2, max_nodes = 6 }
    prod = { instance_size = "t3.xlarge", min_nodes = 3, max_nodes = 20 }
  }
  current = local.env_config[terraform.workspace]
}
```
- Use `terraform.workspace` for env-specific logic
- Alternative: Separate root modules per env with shared modules

### Policy as Code (OPA/Rego)
```rego
# policies/terraform/required_tags.rego
package terraform

deny[msg] {
  resource := input.planned_values.root_module.resources[_]
  resource.type == "aws_instance"
  not resource.values.tags.Environment
  msg := sprintf("Resource %s missing required tag: Environment", [resource.address])
}

deny[msg] {
  resource := input.planned_values.root_module.resources[_]
  resource.type == "aws_s3_bucket"
  not resource.values.versioning.enabled
  msg := sprintf("Bucket %s must have versioning enabled", [resource.address])
}
```
```bash
# In CI: terraform plan -out=tfplan && terraform show -json tfplan | opa eval -i -d policies/terraform "data.terraform.deny"
```

### Secrets Management
- **Never in state**: Use `sensitive = true` on outputs, but state still contains values
- **External secrets**: HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, GCP Secret Manager
- **SOPS**: Encrypt secrets files with age/GPG, decrypt at runtime
- **Terraform providers**: `hashicorp/vault`, `aws/secretsmanager`, `azure/keyvault`

## Pulumi Patterns

### Component Resources
```typescript
// components/vpc.ts
import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";

export interface VpcArgs {
  cidrBlock: string;
  publicSubnetCidrs: string[];
  privateSubnetCidrs: string[];
  tags?: pulumi.Input<{ [key: string]: pulumi.Input<string> }>;
}

export class Vpc extends pulumi.ComponentResource {
  public readonly vpc: aws.ec2.Vpc;
  public readonly publicSubnets: aws.ec2.Subnet[];
  public readonly privateSubnets: aws.ec2.Subnet[];
  public readonly natGateways: aws.ec2.NatGateway[];

  constructor(name: string, args: VpcArgs, opts?: pulumi.ComponentResourceOptions) {
    super("custom:components:Vpc", name, {}, opts);

    this.vpc = new aws.ec2.Vpc(`${name}-vpc`, {
      cidrBlock: args.cidrBlock,
      enableDnsHostnames: true,
      enableDnsSupport: true,
      tags: { ...args.tags, Name: name },
    }, { parent: this });

    // ... create subnets, NAT gateways, route tables
  }
}
```

### Stack References
```typescript
// infra/eks/index.ts
import * as pulumi from "@pulumi/pulumi";
import { Vpc } from "../../components/vpc";

const vpcStack = new pulumi.StackReference("org/vpc/prod");
const vpcId = vpcStack.getOutput("vpcId");
const privateSubnetIds = vpcStack.getOutput("privateSubnetIds");

const cluster = new eks.Cluster("prod", {
  vpcId,
  privateSubnetIds,
  // ...
});
```

### CrossGuard (Policy as Code)
```typescript
// policies/guardrails.ts
import { PolicyPack, validateResourceOfType } from "@pulumi/policy";

new PolicyPack({
  name: "aws-guardrails",
  enforcementLevel: "mandatory",
  policies: [
    {
      name: "s3-versioning",
      description: "S3 buckets must have versioning enabled",
      enforcementLevel: "mandatory",
      validateResource: validateResourceOfType(aws.s3.Bucket, (bucket, args, reportViolation) => {
        if (!bucket.versioning?.enabled) {
          reportViolation("S3 bucket must have versioning enabled");
        }
      }),
    },
  ],
});
```

## CloudFormation / CDK

### CDK (Preferred Over Raw CloudFormation)
```typescript
// lib/vpc-stack.ts
import * as cdk from "aws-cdk-lib";
import * as ec2 from "aws-cdk-lib/aws-ec2";

export class VpcStack extends cdk.Stack {
  public readonly vpc: ec2.Vpc;

  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    this.vpc = new ec2.Vpc(this, "Vpc", {
      maxAzs: 3,
      natGateways: 2,
      subnetConfiguration: [
        { name: "public", subnetType: ec2.SubnetType.PUBLIC, cidrMask: 24 },
        { name: "private", subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS, cidrMask: 24 },
        { name: "isolated", subnetType: ec2.SubnetType.PRIVATE_ISOLATED, cidrMask: 24 },
      ],
    });
  }
}
```

### Nested Stacks
```typescript
// lib/main-stack.ts
import * as cdk from "aws-cdk-lib";
import { VpcStack } from "./vpc-stack";
import { EksStack } from "./eks-stack";

export class MainStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const vpc = new VpcStack(this, "Vpc");
    new EksStack(this, "Eks", { vpc: vpc.vpc });
  }
}
```

## CI/CD for IaC

### Terraform Pipeline
```yaml
# .github/workflows/terraform.yml
jobs:
  plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
      - run: terraform fmt -check
      - run: terraform init
      - run: terraform validate
      - run: terraform plan -out=tfplan
      - uses: actions/upload-artifact@v4
        with:
          name: tfplan
          path: tfplan

  policy-check:
    needs: plan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: tfplan
      - run: terraform show -json tfplan | opa eval -i -d policies/terraform "data.terraform.deny[x]"

  apply:
    needs: [plan, policy-check]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: tfplan
      - run: terraform apply -auto-approve tfplan
```

---

## Validation Checklist

- [ ] All modules have `versions.tf`, `variables.tf` with validations, `outputs.tf`
- [ ] Remote state backend configured with locking
- [ ] State separated per environment
- [ ] Drift detection scheduled (daily/weekly)
- [ ] OPA policies for required tags, security configs, naming
- [ ] Secrets never in state (Vault, Secrets Manager, SOPS)
- [ ] Module tests (Terratest/kitchen-terraform)
- [ ] `terraform fmt -check` and `validate` in CI
- [ ] Plan artifact uploaded, policy check runs before apply
- [ ] Apply requires approval for production