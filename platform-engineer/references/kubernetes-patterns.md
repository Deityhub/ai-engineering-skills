# Kubernetes Patterns

## Cluster Management

### Managed Control Planes
| Provider | Service | Recommended Version |
|----------|---------|---------------------|
| AWS | EKS | 1.28+ (extended support) |
| GCP | GKE | Autopilot or Standard 1.28+ |
| Azure | AKS | 1.28+ (managed) |

**Never self-manage control plane** unless regulatory requirement. Managed = patches, upgrades, HA handled.

### Node Pool Strategy
```yaml
# Separate node pools for workload isolation
nodePools:
  - name: system
    instanceType: t3.medium
    minSize: 2
    maxSize: 5
    labels:
      workload: system
    taints:
      - key: "system"
        effect: "NoSchedule"
  
  - name: general
    instanceType: t3.large
    minSize: 3
    maxSize: 50
    labels:
      workload: general
    # Spot instances for cost savings
    spot: true
    fallbackToOnDemand: true
  
  - name: gpu
    instanceType: g5.xlarge
    minSize: 0
    maxSize: 10
    labels:
      workload: ml
      nvidia.com/gpu: "true"
    taints:
      - key: "nvidia.com/gpu"
        effect: "NoSchedule"
```

### Cluster API (CAPI)
```yaml
# cluster.yaml
apiVersion: cluster.x-k8s.io/v1beta1
kind: Cluster
metadata:
  name: prod-cluster
  namespace: clusters
spec:
  clusterNetwork:
    services:
      cidrBlocks: ["10.96.0.0/12"]
    pods:
      cidrBlocks: ["192.168.0.0/16"]
    serviceDomain: "cluster.local"
  controlPlaneRef:
    kind: AWSManagedControlPlane
    name: prod-control-plane
  infrastructureRef:
    kind: AWSCluster
    name: prod-infrastructure
---
apiVersion: controlplane.cluster.x-k8s.io/v1beta1
kind: AWSManagedControlPlane
metadata:
  name: prod-control-plane
spec:
  region: us-east-1
  sshKeyName: "prod-bastion"
  version: "1.28"
---
apiVersion: infrastructure.cluster.x-k8s.io/v1beta1
kind: AWSCluster
metadata:
  name: prod-infrastructure
spec:
  region: us-east-1
  networkSpec:
    vpc:
      id: "vpc-12345"
    subnets:
      - id: "subnet-abc"
        type: Private
      - id: "subnet-def"
        type: Public
```

## GitOps (ArgoCD / Flux)

### ArgoCD Application
```yaml
# applications/prod-api.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: api
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: production
  source:
    repoURL: https://github.com/org/infra.git
    targetRevision: main
    path: overlays/prod/api
    helm:
      valueFiles:
        - values.yaml
        - values-prod.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: api
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
      allowEmpty: false
    syncOptions:
      - CreateNamespace=true
      - PrunePropagationPolicy=foreground
      - PruneLast=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
```

### Flux Kustomization
```yaml
# flux-system/kustomization.yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: api
  namespace: flux-system
spec:
  interval: 10m
  path: ./clusters/prod/api
  prune: true
  wait: true
  timeout: 5m
  sourceRef:
    kind: GitRepository
    name: infra
  decryption:
    provider: sops
    secretRef:
      name: sops-gpg
```

### Helm Values Schema
```json
# charts/api/values.schema.json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "replicaCount": {
      "type": "integer",
      "minimum": 1,
      "maximum": 100,
      "default": 3
    },
    "image": {
      "type": "object",
      "properties": {
        "repository": { "type": "string", "pattern": "^[a-z0-9./_-]+$" },
        "tag": { "type": "string", "pattern": "^[a-zA-Z0-9._-]+$" },
        "pullPolicy": { "type": "string", "enum": ["Always", "IfNotPresent", "Never"] }
      },
      "required": ["repository", "tag"]
    },
    "resources": {
      "type": "object",
      "properties": {
        "limits": {
          "type": "object",
          "properties": {
            "cpu": { "type": "string", "pattern": "^[0-9]+m?$" },
            "memory": { "type": "string", "pattern": "^[0-9]+[KMGT]i?$" }
          }
        },
        "requests": { "$ref": "#/properties/resources/properties/limits" }
      }
    }
  },
  "required": ["image"]
}
```

## Workload Best Practices

### Deployment with Probes & Resources
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  labels:
    app: api
    version: v1.2.3
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 0
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
        version: v1.2.3
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
        prometheus.io/path: "/metrics"
    spec:
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: DoNotSchedule
          labelSelector:
            matchLabels:
              app: api
      containers:
        - name: api
          image: ghcr.io/org/api:v1.2.3
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 8080
              name: http
          env:
            - name: ENV
              value: "production"
          resources:
            requests:
              cpu: "250m"
              memory: "256Mi"
            limits:
              cpu: "1000m"
              memory: "1Gi"
          livenessProbe:
            httpGet:
              path: /health/live
              port: 8080
            initialDelaySeconds: 10
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 3
          startupProbe:
            httpGet:
              path: /health/startup
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 30
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
```

### Horizontal Pod Autoscaler (HPA)
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  minReplicas: 3
  maxReplicas: 50
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Percent
          value: 10
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
        - type: Percent
          value: 100
          periodSeconds: 15
        - type: Pods
          value: 4
          periodSeconds: 15
      selectPolicy: Max
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
    - type: Pods
      pods:
        metric:
          name: http_requests_per_second
        target:
          type: AverageValue
          averageValue: "1000"
```

### Pod Disruption Budget
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: api
```

## Operators & CRDs

### Controller-runtime Scaffold
```bash
# Initialize operator project
kubebuilder init --domain example.com --repo github.com/org/api-operator

# Create API
kubebuilder create api --group apps --version v1 --kind NotificationService --resource --controller
```

### Reconcile Loop (Idempotent)
```go
func (r *NotificationServiceReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    log := log.FromContext(ctx)
    
    // 1. Fetch desired state
    var ns apps.NotificationService
    if err := r.Get(ctx, req.NamespacedName, &ns); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }
    
    // 2. Check deletion
    if !ns.DeletionTimestamp.IsZero() {
        return r.handleDeletion(ctx, &ns)
    }
    
    // 3. Ensure finalizer
    if !controllerutil.ContainsFinalizer(&ns, finalizerName) {
        controllerutil.AddFinalizer(&ns, finalizerName)
        return ctrl.Result{}, r.Update(ctx, &ns)
    }
    
    // 4. Reconcile child resources (Deployment, Service, ConfigMap, etc.)
    desiredDeployment := r.buildDeployment(&ns)
    if err := ctrl.SetControllerReference(&ns, desiredDeployment, r.Scheme); err != nil {
        return ctrl.Result{}, err
    }
    
    existingDeployment := &appsv1.Deployment{}
    err := r.Get(ctx, client.ObjectKeyFromObject(desiredDeployment), existingDeployment)
    if err != nil && errors.IsNotFound(err) {
        log.Info("Creating Deployment")
        return ctrl.Result{}, r.Create(ctx, desiredDeployment)
    } else if err != nil {
        return ctrl.Result{}, err
    }
    
    // 5. Update if needed (compare spec)
    if !deploymentEqual(desiredDeployment, existingDeployment) {
        log.Info("Updating Deployment")
        existingDeployment.Spec = desiredDeployment.Spec
        return ctrl.Result{}, r.Update(ctx, existingDeployment)
    }
    
    // 6. Update status
    ns.Status.Replicas = existingDeployment.Status.ReadyReplicas
    ns.Status.Conditions = []metav1.Condition{
        {Type: "Ready", Status: metav1.ConditionTrue, Reason: "Reconciled", Message: "All resources synced"},
    }
    return ctrl.Result{RequeueAfter: 30 * time.Second}, r.Status().Update(ctx, &ns)
}
```

### Webhooks (Validating + Mutating)
```go
// Validating webhook
func (r *NotificationService) ValidateCreate() error {
    if ns.Spec.Replicas > 100 {
        return fmt.Errorf("replicas cannot exceed 100")
    }
    if ns.Spec.Image == "" {
        return fmt.Errorf("image is required")
    }
    return nil
}

// Mutating webhook - set defaults
func (r *NotificationService) Default() {
    if ns.Spec.Replicas == 0 {
        ns.Spec.Replicas = 3
    }
    if ns.Spec.Resources.Requests.Cpu == "" {
        ns.Spec.Resources.Requests.Cpu = "250m"
    }
}
```

## Service Mesh (Istio)

### mTLS (STRICT Mode)
```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: istio-system
spec:
  mtls:
    mode: STRICT
```

### Traffic Management (Canary)
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: api
spec:
  hosts:
    - api
  http:
    - match:
        - headers:
            x-canary:
              exact: "true"
      route:
        - destination:
            host: api
            subset: canary
    - route:
        - destination:
            host: api
            subset: stable
          weight: 95
        - destination:
            host: api
            subset: canary
          weight: 5
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: api
spec:
  host: api
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 1000
      http:
        h2UpgradePolicy: UPGRADE
        http1MaxPendingRequests: 1000
        http2MaxRequests: 1000
    circuitBreaker:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 60s
      maxEjectionPercent: 50
  subsets:
    - name: stable
      labels:
        version: stable
    - name: canary
      labels:
        version: canary
```

### Authorization (Zero Trust)
```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: api-authz
  namespace: api
spec:
  selector:
    matchLabels:
      app: api
  rules:
    - from:
        - source:
            principals: ["cluster.local/ns/frontend/sa/frontend"]
        - source:
            namespaces: ["monitoring"]
      to:
        - operation:
            methods: ["GET", "POST"]
            paths: ["/api/*"]
```

## Security Hardening

### Pod Security Standards (Restricted)
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: api
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### Network Policies
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-ingress
  namespace: api
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: frontend
        - podSelector:
            matchLabels:
              app: ingress-nginx
      ports:
        - protocol: TCP
          port: 8080
```

### Kyverno Policies
```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-resources
spec:
  validationFailureAction: Enforce
  rules:
    - name: require-resource-limits
      match:
        any:
          - resources:
              kinds: ["Deployment", "StatefulSet", "DaemonSet", "Job", "CronJob"]
      validate:
        message: "All containers must have resource requests and limits"
        pattern:
          spec:
            template:
              spec:
                containers:
                  - resources:
                      requests:
                        cpu: "?*"
                        memory: "?*"
                      limits:
                        cpu: "?*"
                        memory: "?*"
```

---

## Validation Checklist

- [ ] Managed control plane (EKS/GKE/AKS) with version ≥1.28
- [ ] Node pools separated by workload type (system, general, spot, GPU)
- [ ] Cluster API for declarative cluster lifecycle (optional)
- [ ] GitOps: ArgoCD or Flux syncing from Git
- [ ] Helm charts with `values.schema.json` validation
- [ ] Deployments: probes (liveness/readiness/startup), resources, topology spread
- [ ] HPA with custom metrics + scale behavior tuning
- [ ] PodDisruptionBudget for HA workloads
- [ ] Operators for custom resources (controller-runtime/Kubebuilder)
- [ ] Service mesh: mTLS STRICT, traffic management, authorization
- [ ] Pod Security Standards: restricted namespace labels
- [ ] NetworkPolicies for ingress/egress control
- [ ] Kyverno/OPA policies for admission control
- [ ] Image scanning in CI (Trivy/Grype) + admission (Kyverno/ImagePolicyWebhook)