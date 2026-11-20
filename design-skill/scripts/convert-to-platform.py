#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cross-Platform Component Converter

Transforms components between platforms (Web → iOS → Android → Flutter → React Native).
Preserves design tokens and accessibility features.

Usage:
    python convert-to-platform.py --input Button.tsx --from react --to swiftui --output Button.swift
    python convert-to-platform.py --dir ./src/components --from react --to flutter --output ./lib/components
    python convert-to-platform.py --input Button.vue --from vue --to react --output ./src/components
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class Platform(Enum):
    HTML = "html"
    REACT = "react"
    VUE = "vue"
    SWIFTUI = "swiftui"
    FLUTTER = "flutter"
    REACT_NATIVE = "react-native"


@dataclass
class ComponentIR:
    """Intermediate representation of a component."""
    name: str
    description: str
    props: List[Dict[str, Any]]
    variants: List[str]
    sizes: List[str]
    states: List[str]
    accessibility: List[str]
    template: str  # HTML-like template
    styles: Dict[str, str]  # Token-based styles
    platform_specific: Dict[str, Any]


class PlatformConverter:
    """Convert components between platforms."""

    def __init__(self):
        self.parsers = {
            Platform.REACT: self._parse_react,
            Platform.VUE: self._parse_vue,
            Platform.HTML: self._parse_html,
            Platform.SWIFTUI: self._parse_swiftui,
            Platform.FLUTTER: self._parse_flutter,
        }
        self.generators = {
            Platform.REACT: self._generate_react,
            Platform.VUE: self._generate_vue,
            Platform.HTML: self._generate_html,
            Platform.SWIFTUI: self._generate_swiftui,
            Platform.FLUTTER: self._generate_flutter,
            Platform.REACT_NATIVE: self._generate_react_native,
        }

    def convert(self, input_path: Path, from_platform: Platform, to_platform: Platform,
                output_path: Path) -> bool:
        """Convert a component file between platforms."""
        try:
            # Parse source
            content = input_path.read_text(encoding='utf-8')
            ir = self.parsers[from_platform](content, input_path.stem)

            # Generate target
            output_content = self.generators[to_platform](ir)

            # Write output
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(output_content, encoding='utf-8')

            return True
        except Exception as e:
            print(f"Error converting {input_path}: {e}", file=sys.stderr)
            return False

    def convert_directory(self, input_dir: Path, from_platform: Platform, to_platform: Platform,
                          output_dir: Path, pattern: str = "**/*") -> Dict[str, int]:
        """Convert all components in a directory."""
        results = {"success": 0, "failed": 0, "skipped": 0}

        # Determine file extensions for source platform
        ext_map = {
            Platform.REACT: [".tsx", ".jsx", ".ts", ".js"],
            Platform.VUE: [".vue"],
            Platform.HTML: [".html", ".htm"],
            Platform.SWIFTUI: [".swift"],
            Platform.FLUTTER: [".dart"],
        }

        extensions = ext_map.get(from_platform, [])
        if not extensions:
            print(f"No extensions mapped for {from_platform.value}", file=sys.stderr)
            return results

        for ext in extensions:
            for input_file in input_dir.glob(f"**/*{ext}"):
                if input_file.is_file():
                    # Determine output extension
                    out_ext_map = {
                        Platform.REACT: ".tsx",
                        Platform.VUE: ".vue",
                        Platform.HTML: ".html",
                        Platform.SWIFTUI: ".swift",
                        Platform.FLUTTER: ".dart",
                        Platform.REACT_NATIVE: ".tsx",
                    }
                    out_ext = out_ext_map.get(to_platform, ".txt")

                    # Preserve directory structure
                    rel_path = input_file.relative_to(input_dir)
                    output_file = output_dir / rel_path.with_suffix(out_ext)

                    if args.verbose:
                        print(f"Converting {input_file} → {output_file}")

                    if self.convert(input_file, from_platform, to_platform, output_file):
                        results["success"] += 1
                    else:
                        results["failed"] += 1

        return results

    # ===== Parsers =====

    def _parse_react(self, content: str, name: str) -> ComponentIR:
        """Parse React component (simplified)."""
        ir = ComponentIR(
            name=name,
            description=f"Converted from React: {name}",
            props=[],
            variants=['primary', 'secondary', 'tertiary', 'ghost', 'danger'],
            sizes=['xs', 'sm', 'md', 'lg', 'xl'],
            states=['default', 'hover', 'active', 'focus', 'disabled', 'loading'],
            accessibility=[],
            template="",
            styles={},
            platform_specific={}
        )

        # Extract props interface
        props_match = re.search(r'interface\s+\w+Props\s*{([^}]+)}', content, re.DOTALL)
        if props_match:
            props_text = props_match.group(1)
            for line in props_text.split('\n'):
                line = line.strip()
                if line and not line.startswith('//') and ':' in line:
                    # Parse prop: name?: type;
                    match = re.match(r'(\w+)\??\s*:\s*([^;]+);', line)
                    if match:
                        prop_name, prop_type = match.groups()
                        ir.props.append({
                            'name': prop_name,
                            'type': prop_type.strip(),
                            'required': '?' not in line.split(':')[0],
                        })

        # Extract template (JSX)
        jsx_match = re.search(r'return\s*\(\s*([\s\S]+?)\s*\);', content)
        if jsx_match:
            ir.template = jsx_match.group(1)

        # Extract CSS classes for styles
        class_matches = re.findall(r'className\s*=\s*["\']([^"\']+)["\']', content)
        ir.styles['classes'] = ' '.join(class_matches)

        return ir

    def _parse_vue(self, content: str, name: str) -> ComponentIR:
        """Parse Vue component (simplified)."""
        ir = ComponentIR(
            name=name,
            description=f"Converted from Vue: {name}",
            props=[],
            variants=['primary', 'secondary', 'tertiary', 'ghost', 'danger'],
            sizes=['xs', 'sm', 'md', 'lg', 'xl'],
            states=['default', 'hover', 'active', 'focus', 'disabled', 'loading'],
            accessibility=[],
            template="",
            styles={},
            platform_specific={}
        )

        # Extract template
        template_match = re.search(r'<template>([\s\S]*?)</template>', content)
        if template_match:
            ir.template = template_match.group(1).strip()

        # Extract script props
        script_match = re.search(r'<script[^>]*>([\s\S]*?)</script>', content)
        if script_match:
            script = script_match.group(1)
            props_match = re.search(r'defineProps<\{([^}]+)\}>', script)
            if props_match:
                props_text = props_match.group(1)
                for line in props_text.split('\n'):
                    line = line.strip()
                    if line and ':' in line:
                        match = re.match(r'(\w+)\??\s*:\s*([^,]+)', line)
                        if match:
                            ir.props.append({
                                'name': match.group(1),
                                'type': match.group(2).strip(),
                                'required': '?' not in line.split(':')[0],
                            })

        # Extract styles
        style_match = re.search(r'<style[^>]*>([\s\S]*?)</style>', content)
        if style_match:
            ir.styles['css'] = style_match.group(1).strip()

        return ir

    def _parse_html(self, content: str, name: str) -> ComponentIR:
        """Parse HTML component (simplified)."""
        ir = ComponentIR(
            name=name,
            description=f"Converted from HTML: {name}",
            props=[],
            variants=['primary', 'secondary', 'tertiary', 'ghost', 'danger'],
            sizes=['xs', 'sm', 'md', 'lg', 'xl'],
            states=['default', 'hover', 'active', 'focus', 'disabled', 'loading'],
            accessibility=[],
            template=content,
            styles={},
            platform_specific={}
        )

        # Extract inline styles
        style_match = re.search(r'<style>([\s\S]*?)</style>', content)
        if style_match:
            ir.styles['css'] = style_match.group(1).strip()

        return ir

    def _parse_swiftui(self, content: str, name: str) -> ComponentIR:
        """Parse SwiftUI component (simplified)."""
        ir = ComponentIR(
            name=name,
            description=f"Converted from SwiftUI: {name}",
            props=[],
            variants=['primary', 'secondary', 'tertiary', 'ghost', 'danger'],
            sizes=['xs', 'sm', 'md', 'lg', 'xl'],
            states=['default', 'hover', 'active', 'focus', 'disabled', 'loading'],
            accessibility=[],
            template="",
            styles={},
            platform_specific={}
        )

        # Extract struct properties
        props_match = re.search(r'struct\s+\w+\s*:\s*View\s*{([^}]+)}', content, re.DOTALL)
        if props_match:
            body = props_match.group(1)
            # Extract init parameters
            init_match = re.search(r'init\s*\(([^)]+)\)', body)
            if init_match:
                params = init_match.group(1)
                for param in params.split(','):
                    param = param.strip()
                    if ':' in param:
                        parts = param.split(':')
                        ir.props.append({
                            'name': parts[0].strip(),
                            'type': parts[1].split('=')[0].strip() if '=' in parts[1] else parts[1].strip(),
                        })

        return ir

    def _parse_flutter(self, content: str, name: str) -> ComponentIR:
        """Parse Flutter component (simplified)."""
        ir = ComponentIR(
            name=name,
            description=f"Converted from Flutter: {name}",
            props=[],
            variants=['primary', 'secondary', 'tertiary', 'ghost', 'danger'],
            sizes=['xs', 'sm', 'md', 'lg', 'xl'],
            states=['default', 'hover', 'active', 'focus', 'disabled', 'loading'],
            accessibility=[],
            template="",
            styles={},
            platform_specific={}
        )

        # Extract constructor parameters
        constructor_match = re.search(r'const\s+\w+\s*\(\s*{([^}]+)}\s*\)', content, re.DOTALL)
        if constructor_match:
            params = constructor_match.group(1)
            for line in params.split(','):
                line = line.strip()
                if ':' in line and not line.startswith('//'):
                    parts = line.split(':')
                    ir.props.append({
                        'name': parts[0].strip().replace('this.', '').replace('required ', ''),
                        'type': parts[1].split('=')[0].strip() if '=' in parts[1] else parts[1].strip(),
                        'required': 'required' in line,
                    })

        return ir

    # ===== Generators =====

    def _generate_react(self, ir: ComponentIR) -> str:
        """Generate React TypeScript component."""
        props_interface = []
        for prop in ir.props:
            required = '' if prop.get('required', False) else '?'
            props_interface.append(f"  {prop['name']}{required}: {prop['type']};")

        variants_str = "', '".join(ir.variants) if ir.variants else "'primary'"
        sizes_str = "', '".join(ir.sizes) if ir.sizes else "'md'"

        return f'''import React, {{ forwardRef }} from 'react';
import './{ir.name}.css';

/**
 * {ir.description}
 *
 * @component
 * @example
 * <{ir.name} variant="primary" size="md" onClick={{handleClick}}>
 *   Click me
 * </{ir.name}>
 */

interface {ir.name}Props {{
  /** Visual variant */
  variant?: '{variants_str}';
  /** Size variant */
  size?: '{sizes_str}';
  /** Disabled state */
  disabled?: boolean;
  /** Loading state */
  loading?: boolean;
  /** Additional CSS classes */
  className?: string;
  /** Test ID for automation */
  "data-testid"?: string;
{chr(10).join(props_interface)}
}}

export const {ir.name} = forwardRef<HTMLButtonElement, {ir.name}Props>(
  (
    {{
      variant = 'primary',
      size = 'md',
      disabled = false,
      loading = false,
      className = '',
      "data-testid": testId,
      children,
      ...rest
    }},
    ref
  ) => {{
    const classNames = [
      '{ir.name.toLowerCase()}',
      `${{ir.name.toLowerCase()}}--variant-${{variant}}`,
      `${{ir.name.toLowerCase()}}--size-${{size}}`,
      className
    ].filter(Boolean).join(' ');

    return (
      <button
        ref={{ref}}
        className={{classNames}}
        disabled={{disabled || loading}}
        aria-disabled={{disabled || loading}}
        aria-busy={{loading}}
        data-testid={{testId}}
        {{...rest}}
      >
        {{loading && <span className="{ir.name.toLowerCase()}__spinner" aria-hidden="true" />}}
        <span className="{ir.name.toLowerCase()}__text">{{children}}</span>
      </button>
    );
  }}
);

{ir.name}.displayName = '{ir.name}';

export default {ir.name};
'''

    def _generate_vue(self, ir: ComponentIR) -> str:
        """Generate Vue component."""
        props_def = []
        props_defaults = []
        for prop in ir.props:
            required = '' if prop.get('required', False) else '?'
            props_def.append(f"  {prop['name']}{required}: {prop['type']};")
            if not prop.get('required', False):
                props_defaults.append(f"    {prop['name']}: undefined,")

        variants_str = "', '".join(ir.variants) if ir.variants else "'primary'"
        sizes_str = "', '".join(ir.sizes) if ir.sizes else "'md'"

        return f'''<script setup lang="ts">
import './{ir.name}.css';

/**
 * {ir.description}
 */

interface Props {{
  variant?: '{variants_str}';
  size?: '{sizes_str}';
  disabled?: boolean;
  loading?: boolean;
  class?: string;
{chr(10).join(props_def)}
}}

const props = withDefaults(defineProps<Props>(), {{
{chr(10).join(props_defaults)}
  variant: 'primary',
  size: 'md',
  disabled: false,
  loading: false,
  class: '',
}});

const emit = defineEmits<{{
  click: [event: MouseEvent];
}}>();

const classNames = computed(() => [
  '{ir.name.toLowerCase()}',
  `${{ir.name.toLowerCase()}}--variant-${{props.variant}}`,
  `${{ir.name.toLowerCase()}}--size-${{props.size}}`,
  props.class,
].filter(Boolean).join(' '));
</script>

<template>
  <button
    :class="classNames"
    :disabled="props.disabled || props.loading"
    :aria-disabled="props.disabled || props.loading"
    :aria-busy="props.loading"
    @click="$emit('click', $event)"
  >
    <span v-if="props.loading" class="{ir.name.toLowerCase()}__spinner" aria-hidden="true" />
    <slot />
  </button>
</template>

<style scoped>
/* {ir.name} - Design Token Usage */
.{ir.name.toLowerCase()} {{
  padding: var(--space-2) var(--space-4);
  gap: var(--space-2);
  background-color: var(--color-primary);
  color: var(--color-text-inverse);
  border: 1px solid transparent;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  line-height: var(--line-height-normal);
  border-radius: var(--radius-button);
  box-shadow: var(--shadow-sm);
  transition: background-color var(--transition-fast), box-shadow var(--transition-fast);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  text-decoration: none;
  white-space: nowrap;
}}

/* Variants */
.{ir.name.toLowerCase()}--variant-primary {{ background-color: var(--color-primary); color: var(--color-text-inverse); }}
.{ir.name.toLowerCase()}--variant-primary:hover:not(:disabled) {{ background-color: var(--color-primary-hover); }}
.{ir.name.toLowerCase()}--variant-secondary {{ background-color: var(--color-secondary); color: var(--color-text-inverse); }}
.{ir.name.toLowerCase()}--variant-secondary:hover:not(:disabled) {{ background-color: var(--color-secondary-hover); }}
.{ir.name.toLowerCase()}--variant-tertiary {{ background-color: transparent; color: var(--color-primary); }}
.{ir.name.toLowerCase()}--variant-tertiary:hover:not(:disabled) {{ background-color: var(--color-surface-hover); }}
.{ir.name.toLowerCase()}--variant-ghost {{ background-color: transparent; color: var(--color-text-primary); }}
.{ir.name.toLowerCase()}--variant-ghost:hover:not(:disabled) {{ background-color: var(--color-surface-hover); }}
.{ir.name.toLowerCase()}--variant-danger {{ background-color: var(--color-error); color: var(--color-text-inverse); }}
.{ir.name.toLowerCase()}--variant-danger:hover:not(:disabled) {{ background-color: var(--color-error); }}

/* Sizes */
.{ir.name.toLowerCase()}--size-xs {{ padding: var(--space-1) var(--space-2); font-size: var(--font-size-xs); min-height: 28px; }}
.{ir.name.toLowerCase()}--size-sm {{ padding: var(--space-2) var(--space-3); font-size: var(--font-size-sm); min-height: 36px; }}
.{ir.name.toLowerCase()}--size-md {{ padding: var(--space-2) var(--space-4); font-size: var(--font-size-sm); min-height: 44px; }}
.{ir.name.toLowerCase()}--size-lg {{ padding: var(--space-3) var(--space-5); font-size: var(--font-size-md); min-height: 48px; }}
.{ir.name.toLowerCase()}--size-xl {{ padding: var(--space-3) var(--space-6); font-size: var(--font-size-lg); min-height: 52px; }}

/* States */
.{ir.name.toLowerCase()}:hover:not(:disabled) {{ background-color: var(--color-primary-hover); }}
.{ir.name.toLowerCase()}:active:not(:disabled) {{ background-color: var(--color-primary-active); }}
.{ir.name.toLowerCase()}:focus-visible {{ outline: 2px solid var(--color-focus-ring); outline-offset: 2px; }}
.{ir.name.toLowerCase()}:disabled {{ background-color: var(--color-primary-disabled); cursor: not-allowed; opacity: 0.6; }}

.{ir.name.toLowerCase()}__spinner {{
  width: 1em; height: 1em;
  border: 2px solid currentColor; border-right-color: transparent;
  border-radius: 50%; animation: {ir.name.toLowerCase()}-spin 0.6s linear infinite;
  margin-right: var(--space-2);
}}
@keyframes {ir.name.toLowerCase()}-spin {{ to {{ transform: rotate(360deg); }} }}
</style>
'''

    def _generate_html(self, ir: ComponentIR) -> str:
        """Generate HTML component with embedded CSS."""
        return f'''<!-- {ir.name} Component -->
<!-- {ir.description} -->

<div class="{ir.name.toLowerCase()} {ir.name.toLowerCase()}--variant-primary {ir.name.toLowerCase()}--size-md">
  <span class="{ir.name.toLowerCase()}__text">{ir.name}</span>
</div>

<style>
/* {ir.name} - Design Token Usage */
.{ir.name.toLowerCase()} {{
  padding: var(--space-2) var(--space-4);
  gap: var(--space-2);
  background-color: var(--color-primary);
  color: var(--color-text-inverse);
  border: 1px solid transparent;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  line-height: var(--line-height-normal);
  border-radius: var(--radius-button);
  box-shadow: var(--shadow-sm);
  transition: background-color var(--transition-fast), box-shadow var(--transition-fast);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  text-decoration: none;
  white-space: nowrap;
}}

/* Variants */
.{ir.name.toLowerCase()}--variant-primary {{ background-color: var(--color-primary); color: var(--color-text-inverse); }}
.{ir.name.toLowerCase()}--variant-primary:hover:not(:disabled) {{ background-color: var(--color-primary-hover); }}
.{ir.name.toLowerCase()}--variant-secondary {{ background-color: var(--color-secondary); color: var(--color-text-inverse); }}
.{ir.name.toLowerCase()}--variant-secondary:hover:not(:disabled) {{ background-color: var(--color-secondary-hover); }}
.{ir.name.toLowerCase()}--variant-tertiary {{ background-color: transparent; color: var(--color-primary); }}
.{ir.name.toLowerCase()}--variant-tertiary:hover:not(:disabled) {{ background-color: var(--color-surface-hover); }}
.{ir.name.toLowerCase()}--variant-ghost {{ background-color: transparent; color: var(--color-text-primary); }}
.{ir.name.toLowerCase()}--variant-ghost:hover:not(:disabled) {{ background-color: var(--color-surface-hover); }}
.{ir.name.toLowerCase()}--variant-danger {{ background-color: var(--color-error); color: var(--color-text-inverse); }}
.{ir.name.toLowerCase()}--variant-danger:hover:not(:disabled) {{ background-color: var(--color-error); }}

/* Sizes */
.{ir.name.toLowerCase()}--size-xs {{ padding: var(--space-1) var(--space-2); font-size: var(--font-size-xs); min-height: 28px; }}
.{ir.name.toLowerCase()}--size-sm {{ padding: var(--space-2) var(--space-3); font-size: var(--font-size-sm); min-height: 36px; }}
.{ir.name.toLowerCase()}--size-md {{ padding: var(--space-2) var(--space-4); font-size: var(--font-size-sm); min-height: 44px; }}
.{ir.name.toLowerCase()}--size-lg {{ padding: var(--space-3) var(--space-5); font-size: var(--font-size-md); min-height: 48px; }}
.{ir.name.toLowerCase()}--size-xl {{ padding: var(--space-3) var(--space-6); font-size: var(--font-size-lg); min-height: 52px; }}

/* States */
.{ir.name.toLowerCase()}:hover:not(:disabled) {{ background-color: var(--color-primary-hover); }}
.{ir.name.toLowerCase()}:active:not(:disabled) {{ background-color: var(--color-primary-active); }}
.{ir.name.toLowerCase()}:focus-visible {{ outline: 2px solid var(--color-focus-ring); outline-offset: 2px; }}
.{ir.name.toLowerCase()}:disabled {{ background-color: var(--color-primary-disabled); cursor: not-allowed; opacity: 0.6; }}
</style>
'''

    def _generate_swiftui(self, ir: ComponentIR) -> str:
        """Generate SwiftUI component."""
        props_params = []
        props_fields = []
        for prop in ir.props:
            default = f" = {prop.get('default', 'false')}" if 'default' in prop else ""
            props_params.append(f"    {prop['name']}: {prop['type']}{default}")
            props_fields.append(f"  private let {prop['name']}: {prop['type']}")

        return f'''import SwiftUI

/// {ir.description}
@available(iOS 15.0, macOS 12.0, *)
public struct {ir.name}: View {{
  public enum Variant {{
    case primary, secondary, tertiary, ghost, danger
  }}

  public enum Size {{
    case xs, sm, md, lg, xl
  }}

{chr(10).join(props_fields)}
  private let variant: Variant
  private let size: Size
  private let isDisabled: Bool
  private let isLoading: Bool
  private let action: () -> Void
  private let label: String

  public init(
    _ label: String,
{chr(10).join(props_params)},
    variant: Variant = .primary,
    size: Size = .md,
    isDisabled: Bool = false,
    isLoading: Bool = false,
    action: @escaping () -> Void
  ) {{
    self.label = label
{chr(10).join([f"    self.{prop['name']} = {prop['name']}" for prop in ir.props])}
    self.variant = variant
    self.size = size
    self.isDisabled = isDisabled
    self.isLoading = isLoading
    self.action = action
  }}

  public var body: some View {{
    Button(action: action) {{
      HStack(spacing: spacing(.space2)) {{
        if isLoading {{
          ProgressView()
            .progressViewStyle(CircularProgressViewStyle(tint: textColor))
            .accessibilityHidden(true)
        }}
        Text(label)
          .font(font)
          .fontWeight(.medium)
      }}
      .padding(.horizontal, horizontalPadding)
      .padding(.vertical, verticalPadding)
      .frame(minWidth: minWidth, minHeight: minHeight)
      .background(backgroundColor)
      .foregroundColor(textColor)
      .cornerRadius(cornerRadius)
      .shadow(color: shadowColor, radius: shadowRadius, x: 0, y: shadowY)
      .opacity(isDisabled || isLoading ? 0.6 : 1.0)
      .animation(.easeInOut(duration: 0.15), value: isDisabled)
    }}
    .disabled(isDisabled || isLoading)
    .accessibilityLabel(label)
    .accessibilityAddTraits(isDisabled ? [.isButton, .isDisabled] : .isButton)
  }}

  // MARK: - Token-based Styling

  private var backgroundColor: Color {{
    switch variant {{
    case .primary: return isDisabled ? Color.disabledBg : Color.primary
    case .secondary: return isDisabled ? Color.disabledBg : Color.secondary
    case .tertiary: return Color.clear
    case .ghost: return Color.clear
    case .danger: return isDisabled ? Color.disabledBg : Color.error
    }}
  }}

  private var textColor: Color {{
    switch variant {{
    case .primary, .danger: return Color.textInverse
    case .secondary: return Color.textPrimary
    case .tertiary, .ghost: return Color.primary
    }}
  }}

  private var font: Font {{
    switch size {{
    case .xs: return .caption2
    case .sm: return .caption
    case .md: return .body
    case .lg: return .title3
    case .xl: return .title2
    }}
  }}

  private var horizontalPadding: CGFloat {{
    switch size {{
    case .xs: return spacing(.space2)
    case .sm: return spacing(.space3)
    case .md: return spacing(.space4)
    case .lg: return spacing(.space5)
    case .xl: return spacing(.space6)
    }}
  }}

  private var verticalPadding: CGFloat {{
    switch size {{
    case .xs: return spacing(.space1)
    case .sm: return spacing(.space2)
    case .md: return spacing(.space2)
    case .lg: return spacing(.space3)
    case .xl: return spacing(.space3)
    }}
  }}

  private var minWidth: CGFloat {{
    switch size {{
    case .xs: return 32
    case .sm: return 44
    case .md: return 44
    case .lg: return 48
    case .xl: return 56
    }}
  }}

  private var minHeight: CGFloat {{
    switch size {{
    case .xs: return 28
    case .sm: return 36
    case .md: return 44
    case .lg: return 48
    case .xl: return 52
    }}
  }}

  private var cornerRadius: CGFloat {{
    radius(.radiusButton)
  }}

  private var shadowColor: Color {{ Color.black.opacity(0.1) }}
  private var shadowRadius: CGFloat {{ 2 }}
  private var shadowY: CGFloat {{ 1 }}

  // MARK: - Token Helpers

  private func spacing(_ token: SpacingToken) -> CGFloat {{
    switch token {{
    case .space1: return 4
    case .space2: return 8
    case .space3: return 12
    case .space4: return 16
    case .space5: return 20
    case .space6: return 24
    case .space8: return 32
    case .space10: return 40
    case .space12: return 48
    case .space16: return 64
    }}
  }}

  private func radius(_ token: RadiusToken) -> CGFloat {{
    switch token {{
    case .radiusButton: return 6
    case .radiusInput: return 6
    case .radiusCard: return 8
    case .radiusModal: return 12
    case .radiusFull: return 9999
    }}
  }}
}}

// MARK: - Design Token Extensions

extension Color {{
  static let primary = Color(hex: "2563EB")
  static let primaryHover = Color(hex: "1D4ED8")
  static let primaryActive = Color(hex: "1E40AF")
  static let primaryDisabled = Color(hex: "93C5FD")
  static let secondary = Color(hex: "64748B")
  static let surface = Color(hex: "FFFFFF")
  static let textPrimary = Color(hex: "0F172A")
  static let textInverse = Color(hex: "F8FAFC")
  static let error = Color(hex: "DC2626")
  static let disabledBg = Color(hex: "F1F5F9")
  static let focusRing = Color(hex: "2563EB")
  static let disabledText = Color(hex: "94A3B8")
}}

private enum SpacingToken {{ case space1, space2, space3, space4, space5, space6, space8, space10, space12, space16 }}
private enum RadiusToken {{ case radiusButton, radiusInput, radiusCard, radiusModal, radiusFull }}

extension Color {{
  init(hex: String) {{
    let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
    var int: UInt64 = 0
    Scanner(string: hex).scanHexInt64(&int)
    let a, r, g, b: UInt64
    switch hex.count {{
    case 3: (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
    case 6: (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
    case 8: (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
    default: (a, r, g, b) = (1, 1, 1, 0)
    }}
    self.init(.sRGB, red: Double(r)/255, green: Double(g)/255, blue: Double(b)/255, opacity: Double(a)/255)
  }}
}}
'''

    def _generate_flutter(self, ir: ComponentIR) -> str:
        """Generate Flutter component."""
        props_fields = []
        props_params = []
        for prop in ir.props:
            required = "required " if prop.get('required', False) else ""
            default = f" = {prop.get('default', '')}" if 'default' in prop else ""
            props_fields.append(f"  final {prop['type']} {prop['name']};")
            props_params.append(f"    {required}this.{prop['name']}{default},")

        return f'''import 'package:flutter/material.dart';

/// {ir.description}
class {ir.name} extends StatelessWidget {{
  const {ir.name}({{
    super.key,
    required this.label,
    this.variant = Variant.primary,
    this.size = Size.md,
    this.disabled = false,
    this.loading = false,
    this.onPressed,
    this.icon,
    this.iconAlignment = IconAlignment.end,
{chr(10).join(props_params)}
  }});

  final String label;
  final Variant variant;
  final Size size;
  final bool disabled;
  final bool loading;
  final VoidCallback? onPressed;
  final Widget? icon;
  final IconAlignment iconAlignment;
{chr(10).join(props_fields)}

  @override
  Widget build(BuildContext context) {{
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Semantics(
      button: true,
      enabled: !disabled && !loading,
      child: _buildButton(context, colorScheme),
    );
  }}

  Widget _buildButton(BuildContext context, ColorScheme colorScheme) {{
    return AnimatedContainer(
      duration: const Duration(milliseconds: 150),
      curve: Curves.easeInOut,
      decoration: BoxDecoration(
        color: _backgroundColor(colorScheme),
        borderRadius: BorderRadius.circular(_cornerRadius),
        border: _border(colorScheme),
        boxShadow: _boxShadow(colorScheme),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: disabled || loading ? null : onPressed,
          borderRadius: BorderRadius.circular(_cornerRadius),
          splashColor: _splashColor(colorScheme),
          highlightColor: _highlightColor(colorScheme),
          child: Padding(
            padding: EdgeInsets.symmetric(
              horizontal: _horizontalPadding,
              vertical: _verticalPadding,
            ),
            child: ConstrainedBox(
              constraints: BoxConstraints(
                minWidth: _minWidth,
                minHeight: _minHeight,
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  if (loading) ...[
                    SizedBox(
                      width: _spinnerSize,
                      height: _spinnerSize,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        valueColor: AlwaysStoppedAnimation<Color>(_textColor(colorScheme)),
                      ),
                    ),
                    SizedBox(width: _iconSpacing),
                  ],
                  if (icon != null && iconAlignment == IconAlignment.start) ...[
                    icon!,
                    SizedBox(width: _iconSpacing),
                  ],
                  Flexible(
                    child: Text(
                      label,
                      style: _textStyle,
                      textAlign: TextAlign.center,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  if (icon != null && iconAlignment == IconAlignment.end) ...[
                    SizedBox(width: _iconSpacing),
                    icon!,
                  ],
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }}

  // MARK: - Token-based Styling

  Color _backgroundColor(ColorScheme colorScheme) {{
    if (disabled) return colorScheme.disabledBg;
    switch (variant) {{
      case Variant.primary: return colorScheme.primary;
      case Variant.secondary: return colorScheme.secondary;
      case Variant.tertiary: return Colors.transparent;
      case Variant.ghost: return Colors.transparent;
      case Variant.danger: return colorScheme.error;
    }}
  }}

  Color _textColor(ColorScheme colorScheme) {{
    if (disabled) return colorScheme.disabledText;
    switch (variant) {{
      case Variant.primary: return colorScheme.onPrimary;
      case Variant.danger: return colorScheme.onError;
      default: return colorScheme.primary;
    }}
  }}

  Border? _border(ColorScheme colorScheme) {{
    if (variant == Variant.ghost || variant == Variant.tertiary) {{
      return Border.all(color: colorScheme.outline, width: 1);
    }}
    return null;
  }}

  List<BoxShadow> _boxShadow(ColorScheme colorScheme) {{
    return [
      BoxShadow(
        color: Colors.black.withOpacity(0.05),
        blurRadius: 2,
        offset: const Offset(0, 1),
      ),
    ];
  }}

  Color _splashColor(ColorScheme colorScheme) {{
    return _textColor(colorScheme).withOpacity(0.1);
  }}

  Color _highlightColor(ColorScheme colorScheme) {{
    return _textColor(colorScheme).withOpacity(0.05);
  }}

  TextStyle get _textStyle => TextStyle(
    fontSize: _fontSize,
    fontWeight: FontWeight.w500,
    color: _textColor(Theme.of(context).colorScheme),
    letterSpacing: 0.25,
  );

  double get _cornerRadius => 6.0; // radiusMd

  double get _horizontalPadding {{
    switch (size) {{
      case Size.xs: return 8.0;  // space2
      case Size.sm: return 12.0; // space3
      case Size.md: return 16.0; // space4
      case Size.lg: return 20.0; // space5
      case Size.xl: return 24.0; // space6
    }}
  }}

  double get _verticalPadding {{
    switch (size) {{
      case Size.xs: return 4.0;  // space1
      case Size.sm: return 8.0;  // space2
      case Size.md: return 8.0;  // space2
      case Size.lg: return 12.0; // space3
      case Size.xl: return 12.0; // space3
    }}
  }}

  double get _minWidth {{
    switch (size) {{
      case Size.xs: return 32.0;
      case Size.sm: return 44.0;
      case Size.md: return 44.0;
      case Size.lg: return 48.0;
      case Size.xl: return 56.0;
    }}
  }}

  double get _minHeight {{
    switch (size) {{
      case Size.xs: return 28.0;
      case Size.sm: return 36.0;
      case Size.md: return 44.0;
      case Size.lg: return 48.0;
      case Size.xl: return 52.0;
    }}
  }}

  double get _fontSize {{
    switch (size) {{
      case Size.xs: return 12.0; // fontSizeXs
      case Size.sm: return 14.0; // fontSizeSm
      case Size.md: return 14.0; // fontSizeMd (buttons use smaller)
      case Size.lg: return 16.0; // fontSizeLg
      case Size.xl: return 18.0; // fontSizeXl
    }}
  }}

  double get _iconSpacing => 8.0; // space2

  double get _spinnerSize => 16.0;
}}

enum Variant {{ primary, secondary, tertiary, ghost, danger }}
enum Size {{ xs, sm, md, lg, xl }}
enum IconAlignment {{ start, end }}

// ColorScheme extension for design tokens
extension DesignTokens on ColorScheme {{
  Color get primary => const Color(0xFF2563EB);
  Color get onPrimary => const Color(0xFFFFFFFF);
  Color get secondary => const Color(0xFF64748B);
  Color get onSecondary => const Color(0xFFFFFFFF);
  Color get error => const Color(0xFFDC2626);
  Color get onError => const Color(0xFFFFFFFF);
  Color get surface => const Color(0xFFFFFFFF);
  Color get onSurface => const Color(0xFF0F172A);
  Color get outline => const Color(0xFFE2E8F0);
  Color get disabledBg => const Color(0xFFF1F5F9);
  Color get disabledText => const Color(0xFF94A3B8);
}}
'''

    def _generate_react_native(self, ir: ComponentIR) -> str:
        """Generate React Native component."""
        # Similar to React but with View/Text instead of div/span
        return self._generate_react(ir).replace(
            'import React', 'import React, { View, Text, StyleSheet } from "react-native";\nimport React'
        ).replace('<button', '<View').replace('</button>', '</View>')


def main():
    parser = argparse.ArgumentParser(
        description="Convert components between platforms preserving design tokens and accessibility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python convert-to-platform.py --input Button.tsx --from react --to swiftui --output Button.swift
  python convert-to-platform.py --dir ./src/components --from react --to flutter --output ./lib/components
  python convert-to-platform.py --input Button.vue --from vue --to react --output ./src/components
        """
    )

    parser.add_argument('--input', '-i', help='Input file or directory')
    parser.add_argument('--from', dest='from_platform', required=True,
                       choices=[p.value for p in Platform],
                       help='Source platform')
    parser.add_argument('--to', dest='to_platform', required=True,
                       choices=[p.value for p in Platform],
                       help='Target platform')
    parser.add_argument('--output', '-o', required=True, help='Output file or directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    if not args.input:
        print("Error: --input required", file=sys.stderr)
        sys.exit(1)

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"Error: Input not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    from_platform = Platform(args.from_platform)
    to_platform = Platform(args.to_platform)

    converter = PlatformConverter()

    if input_path.is_file():
        if args.verbose:
            print(f"Converting {input_path} from {from_platform.value} to {to_platform.value}")

        success = converter.convert(input_path, from_platform, to_platform, output_path)
        if success:
            print(f"[OK] Converted: {output_path}")
        else:
            print(f"[FAIL] Failed: {input_path}")
            sys.exit(1)
    else:
        if args.verbose:
            print(f"Converting directory {input_path} from {from_platform.value} to {to_platform.value}")

        results = converter.convert_directory(input_path, from_platform, to_platform, output_path)

        print(f"\n[STATS] Conversion Results:")
        print(f"   [OK] Success: {results['success']}")
        print(f"   [FAIL] Failed: {results['failed']}")
        print(f"   ⏭️  Skipped: {results['skipped']}")

        if results['failed'] > 0:
            sys.exit(1)


if __name__ == '__main__':
    main()