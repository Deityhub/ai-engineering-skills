#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Component Generator

Scaffolds accessible, token-compliant components from specifications.
Supports multiple frameworks: HTML/CSS, React, Vue, SwiftUI, Flutter.

Usage:
    python generate-component.py --spec component-spec.md --framework react --output ./src/components
    python generate-component.py --spec page-spec.md --framework html --output ./components
    python generate-component.py --interactive --framework vue
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from string import Template


@dataclass
class ComponentSpec:
    name: str
    description: str
    props: List[Dict[str, Any]] = field(default_factory=list)
    variants: List[str] = field(default_factory=list)
    sizes: List[str] = field(default_factory=list)
    states: List[str] = field(default_factory=list)
    accessibility: List[str] = field(default_factory=list)
    framework_specific: Dict[str, Any] = field(default_factory=dict)


class ComponentGenerator:
    """Generate component code from specifications."""

    def __init__(self):
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, Dict[str, str]]:
        """Load component templates for each framework."""
        return {
            'html': self._html_templates(),
            'react': self._react_templates(),
            'vue': self._vue_templates(),
            'swiftui': self._swiftui_templates(),
            'flutter': self._flutter_templates(),
        }

    def _html_templates(self) -> Dict[str, str]:
        return {
            'component': '''<!-- ${name} Component -->
${accessibility_notes}
<div class="${class_name}${variant_classes}${size_classes}" ${aria_attributes}>
  ${children}
</div>

<style>
/* ${name} - Design Token Usage */
.${class_name} {
  /* Spacing */
  padding: var(--space-2) var(--space-4);
  gap: var(--space-2);

  /* Color */
  background-color: var(--color-primary);
  color: var(--color-text-inverse);
  border: 1px solid transparent;

  /* Typography */
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  line-height: var(--line-height-normal);

  /* Border Radius */
  border-radius: var(--radius-button);

  /* Shadows */
  box-shadow: var(--shadow-sm);

  /* Transitions */
  transition: background-color var(--transition-fast),
              box-shadow var(--transition-fast),
              transform var(--transition-fast);
}

/* Variants */
${variant_styles}

/* Sizes */
${size_styles}

/* States */
.${class_name}:hover:not(:disabled) {
  background-color: var(--color-primary-hover);
}

.${class_name}:active:not(:disabled) {
  background-color: var(--color-primary-active);
}

.${class_name}:focus-visible {
  outline: 2px solid var(--color-focus-ring);
  outline-offset: 2px;
}

.${class_name}:disabled {
  background-color: var(--color-primary-disabled);
  cursor: not-allowed;
  opacity: 0.6;
}

/* Dark mode - automatic via CSS custom properties */
</style>''',

            'button': '''<button
  class="${class_name}${variant_classes}${size_classes}"
  type="${type}"
  ${disabled_attr}
  ${aria_attributes}
>
  ${icon_before}
  <span class="${class_name}__text">${label}</span>
  ${icon_after}
</button>''',

            'input': '''<div class="${class_name}__wrapper">
  <label class="${class_name}__label" for="${id}">${label}${required_mark}</label>
  <input
    class="${class_name}__input${error_class}"
    id="${id}"
    type="${type}"
    ${placeholder_attr}
    ${value_attr}
    ${disabled_attr}
    ${required_attr}
    ${aria_attrs}
  />
  ${error_message}
  ${helper_text}
</div>''',

            'card': '''<article class="${class_name}${variant_classes}">
  ${header}
  <div class="${class_name}__content">
    ${children}
  </div>
  ${footer}
</article>''',
        }

    def _react_templates(self) -> Dict[str, str]:
        return {
            'component': '''import React, { forwardRef } from 'react';
import './${name}.css';

${accessibility_notes}
/**
 * ${description}
 *
 * @component
 * @example
 * <${name} variant="primary" size="md" onClick={handleClick}>
 *   Click me
 * </${name}>
 */

interface ${name}Props {
  /** Visual variant */
  variant?: '${' | '.join(${variants})}';
  /** Size variant */
  size?: '${' | '.join(${sizes})}';
  /** Disabled state */
  disabled?: boolean;
  /** Loading state */
  loading?: boolean;
  /** Additional CSS classes */
  className?: string;
  /** Test ID for automation */
  "data-testid"?: string;
  ${extra_props}
}

export const ${name} = forwardRef<HTMLButtonElement, ${name}Props>(
  (
    {
      variant = 'primary',
      size = 'md',
      disabled = false,
      loading = false,
      className = '',
      "data-testid": testId,
      children,
      ...rest
    },
    ref
  ) => {
    const classNames = [
      '${name}',
      \`${name}--variant-\${variant}\`,
      \`${name}--size-\${size}\`,
      className
    ].filter(Boolean).join(' ');

    return (
      <button
        ref={ref}
        className={classNames}
        disabled={disabled || loading}
        aria-disabled={disabled || loading}
        aria-busy={loading}
        data-testid={testId}
        {...rest}
      >
        {loading && <span className="${name}__spinner" aria-hidden="true" />}
        <span className="${name}__text">{children}</span>
      </button>
    );
  }
);

${name}.displayName = '${name}';

export default ${name};''',

            'button': '''import React, { forwardRef } from 'react';
import './Button.css';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'tertiary' | 'ghost' | 'danger';
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  loading?: boolean;
  iconOnly?: boolean;
  startIcon?: React.ReactNode;
  endIcon?: React.ReactNode;
  fullWidth?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({
    variant = 'primary',
    size = 'md',
    loading = false,
    iconOnly = false,
    startIcon,
    endIcon,
    fullWidth = false,
    disabled = false,
    className = '',
    children,
    ...rest
  }, ref) => {
    const classNames = [
      'button',
      `button--variant-${variant}`,
      `button--size-${size}`,
      { 'button--icon-only': iconOnly, 'button--full-width': fullWidth, 'button--loading': loading },
      className
    ].filter(Boolean).join(' ');

    return (
      <button
        ref={ref}
        className={classNames}
        disabled={disabled || loading}
        aria-disabled={disabled || loading}
        aria-busy={loading}
        {...rest}
      >
        {loading && <span className="button__spinner" aria-hidden="true" />}
        {!iconOnly && startIcon && <span className="button__icon button__icon--start">{startIcon}</span>}
        <span className="button__text">{children}</span>
        {!iconOnly && endIcon && <span className="button__icon button__icon--end">{endIcon}</span>}
      </button>
    );
  }
);

Button.displayName = 'Button';
export default Button;''',

            'input': '''import React, { forwardRef } from 'react';
import './Input.css';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
  helperText?: string;
  startAdornment?: React.ReactNode;
  endAdornment?: React.ReactNode;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({
    label,
    error,
    helperText,
    startAdornment,
    endAdornment,
    id,
    className = '',
    disabled = false,
    required = false,
    ...rest
  }, ref) => {
    const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;
    const errorId = error ? `${inputId}-error` : undefined;
    const helperId = helperText ? `${inputId}-helper` : undefined;

    const describedBy = [errorId, helperId].filter(Boolean).join(' ') || undefined;

    return (
      <div className={`input-wrapper ${className}`}>
        <label htmlFor={inputId} className="input__label">
          {label}
          {required && <span className="input__required" aria-hidden="true">*</span>}
        </label>
        <div className="input__field-wrapper">
          {startAdornment && <span className="input__adornment input__adornment--start">{startAdornment}</span>}
          <input
            ref={ref}
            id={inputId}
            className={`input__input ${error ? 'input__input--error' : ''}`}
            disabled={disabled}
            required={required}
            aria-invalid={error ? 'true' : 'false'}
            aria-describedby={describedBy}
            {...rest}
          />
          {endAdornment && <span className="input__adornment input__adornment--end">{endAdornment}</span>}
        </div>
        {error && (
          <span id={errorId} className="input__error" role="alert" aria-live="polite">
            {error}
          </span>
        )}
        {helperText && !error && (
          <span id={helperId} className="input__helper">
            {helperText}
          </span>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
export default Input;''',

            'css': '''.${name} {
  /* Spacing */
  padding: var(--space-2) var(--space-4);
  gap: var(--space-2);

  /* Color */
  background-color: var(--color-primary);
  color: var(--color-text-inverse);
  border: 1px solid transparent;

  /* Typography */
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  line-height: var(--line-height-normal);

  /* Border Radius */
  border-radius: var(--radius-button);

  /* Shadows */
  box-shadow: var(--shadow-sm);

  /* Transitions */
  transition: background-color var(--transition-fast),
              box-shadow var(--transition-fast),
              transform var(--transition-fast);

  /* Layout */
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  text-decoration: none;
  white-space: nowrap;
}

/* Variants */
${variant_styles}

/* Sizes */
${size_styles}

/* States */
.${name}:hover:not(:disabled) {
  background-color: var(--color-primary-hover);
}

.${name}:active:not(:disabled) {
  background-color: var(--color-primary-active);
}

.${name}:focus-visible {
  outline: 2px solid var(--color-focus-ring);
  outline-offset: 2px;
}

.${name}:disabled {
  background-color: var(--color-primary-disabled);
  cursor: not-allowed;
  opacity: 0.6;
}

/* Icon only */
.${name}--icon-only {
  padding: var(--space-2);
}

/* Loading spinner */
.${name}__spinner {
  width: 1em;
  height: 1em;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: ${name}-spin 0.6s linear infinite;
  margin-right: var(--space-2);
}

@keyframes ${name}-spin {
  to { transform: rotate(360deg); }
}''',
        }

    def _vue_templates(self) -> Dict[str, str]:
        return {
            'component': '''<script setup lang="ts">
import './${name}.css';

${accessibility_notes}
/**
 * ${description}
 */

interface Props {
  variant?: '${' | '.join(${variants})}';
  size?: '${' | '.join(${sizes})}';
  disabled?: boolean;
  loading?: boolean;
  class?: string;
  ${extra_props}
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  disabled: false,
  loading: false,
  class: '',
});

const emit = defineEmits<{
  click: [event: MouseEvent];
}>();

const classNames = computed(() => [
  '${name}',
  `${name}--variant-${props.variant}`,
  `${name}--size-${props.size}`,
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
    <span v-if="props.loading" class="${name}__spinner" aria-hidden="true" />
    <slot />
  </button>
</template>

<style scoped>
/* ${name} - Design Token Usage */
.${name} {
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
}

/* Variants */
${variant_styles}

/* Sizes */
${size_styles}

/* States */
.${name}:hover:not(:disabled) { background-color: var(--color-primary-hover); }
.${name}:active:not(:disabled) { background-color: var(--color-primary-active); }
.${name}:focus-visible { outline: 2px solid var(--color-focus-ring); outline-offset: 2px; }
.${name}:disabled { background-color: var(--color-primary-disabled); cursor: not-allowed; opacity: 0.6; }

.${name}__spinner {
  width: 1em; height: 1em;
  border: 2px solid currentColor; border-right-color: transparent;
  border-radius: 50%; animation: ${name}-spin 0.6s linear infinite;
  margin-right: var(--space-2);
}
@keyframes ${name}-spin { to { transform: rotate(360deg); } }
</style>''',
        }

    def _swiftui_templates(self) -> Dict[str, str]:
        return {
            'component': '''import SwiftUI

${accessibility_notes}
/// ${description}
@available(iOS 15.0, macOS 12.0, *)
public struct ${name}: View {
  public enum Variant {
    case primary, secondary, tertiary, ghost, danger
  }

  public enum Size {
    case xs, sm, md, lg, xl
  }

  private let variant: Variant
  private let size: Size
  private let isDisabled: Bool
  private let isLoading: Bool
  private let action: () -> Void
  private let label: String

  public init(
    _ label: String,
    variant: Variant = .primary,
    size: Size = .md,
    isDisabled: Bool = false,
    isLoading: Bool = false,
    action: @escaping () -> Void
  ) {
    self.label = label
    self.variant = variant
    self.size = size
    self.isDisabled = isDisabled
    self.isLoading = isLoading
    self.action = action
  }

  public var body: some View {
    Button(action: action) {
      HStack(spacing: spacing(.space2)) {
        if isLoading {
          ProgressView()
            .progressViewStyle(CircularProgressViewStyle(tint: textColor))
            .accessibilityHidden(true)
        }
        Text(label)
          .font(font)
          .fontWeight(.medium)
      }
      .padding(.horizontal, horizontalPadding)
      .padding(.vertical, verticalPadding)
      .frame(minWidth: minWidth, minHeight: minHeight)
      .background(backgroundColor)
      .foregroundColor(textColor)
      .cornerRadius(cornerRadius)
      .shadow(color: shadowColor, radius: shadowRadius, x: 0, y: shadowY)
      .opacity(isDisabled || isLoading ? 0.6 : 1.0)
      .animation(.easeInOut(duration: 0.15), value: isDisabled)
    }
    .disabled(isDisabled || isLoading)
    .accessibilityLabel(label)
    .accessibilityAddTraits(isDisabled ? [.isButton, .isDisabled] : .isButton)
  }

  // MARK: - Token-based Styling

  private var backgroundColor: Color {
    switch variant {
    case .primary: return isDisabled ? Color.disabledBg : Color.primary
    case .secondary: return isDisabled ? Color.disabledBg : Color.secondary
    case .tertiary: return Color.clear
    case .ghost: return Color.clear
    case .danger: return isDisabled ? Color.disabledBg : Color.error
    }
  }

  private var textColor: Color {
    switch variant {
    case .primary, .danger: return Color.textInverse
    case .secondary: return Color.textPrimary
    case .tertiary, .ghost: return Color.primary
    }
  }

  private var font: Font {
    switch size {
    case .xs: return .caption2
    case .sm: return .caption
    case .md: return .body
    case .lg: return .title3
    case .xl: return .title2
    }
  }

  private var horizontalPadding: CGFloat {
    switch size {
    case .xs: return spacing(.space2)
    case .sm: return spacing(.space3)
    case .md: return spacing(.space4)
    case .lg: return spacing(.space5)
    case .xl: return spacing(.space6)
    }
  }

  private var verticalPadding: CGFloat {
    switch size {
    case .xs: return spacing(.space1)
    case .sm: return spacing(.space2)
    case .md: return spacing(.space2)
    case .lg: return spacing(.space3)
    case .xl: return spacing(.space3)
    }
  }

  private var minWidth: CGFloat {
    switch size {
    case .xs: return 32
    case .sm: return 44
    case .md: return 44
    case .lg: return 48
    case .xl: return 56
    }
  }

  private var minHeight: CGFloat {
    switch size {
    case .xs: return 28
    case .sm: return 36
    case .md: return 44
    case .lg: return 48
    case .xl: return 52
    }
  }

  private var cornerRadius: CGFloat {
    radius(.radiusButton)
  }

  private var shadowColor: Color { Color.black.opacity(0.1) }
  private var shadowRadius: CGFloat { 2 }
  private var shadowY: CGFloat { 1 }

  // MARK: - Token Helpers

  private func spacing(_ token: SpacingToken) -> CGFloat {
    // Map to design tokens
    switch token {
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
    }
  }

  private func radius(_ token: RadiusToken) -> CGFloat {
    switch token {
    case .radiusButton: return 6
    case .radiusInput: return 6
    case .radiusCard: return 8
    case .radiusModal: return 12
    case .radiusFull: return 9999
    }
  }
}

// MARK: - Design Token Extensions

extension Color {
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
}

private enum SpacingToken { case space1, space2, space3, space4, space5, space6, space8, space10, space12, space16 }
private enum RadiusToken { case radiusButton, radiusInput, radiusCard, radiusModal, radiusFull }

extension Color {
  init(hex: String) {
    let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
    var int: UInt64 = 0
    Scanner(string: hex).scanHexInt64(&int)
    let a, r, g, b: UInt64
    switch hex.count {
    case 3: (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
    case 6: (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
    case 8: (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
    default: (a, r, g, b) = (1, 1, 1, 0)
    }
    self.init(.sRGB, red: Double(r)/255, green: Double(g)/255, blue: Double(b)/255, opacity: Double(a)/255)
  }
}''',
        }

    def _flutter_templates(self) -> Dict[str, str]:
        return {
            'component': '''import 'package:flutter/material.dart';

${accessibility_notes}
/// ${description}
class ${name} extends StatelessWidget {
  const ${name}({
    super.key,
    required this.label,
    this.variant = Variant.primary,
    this.size = Size.md,
    this.disabled = false,
    this.loading = false,
    this.onPressed,
    this.icon,
    this.iconAlignment = IconAlignment.end,
  });

  final String label;
  final Variant variant;
  final Size size;
  final bool disabled;
  final bool loading;
  final VoidCallback? onPressed;
  final Widget? icon;
  final IconAlignment iconAlignment;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Semantics(
      button: true,
      enabled: !disabled && !loading,
      child: _buildButton(context, colorScheme),
    );
  }

  Widget _buildButton(BuildContext context, ColorScheme colorScheme) {
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
  }

  // MARK: - Token-based Styling

  Color _backgroundColor(ColorScheme colorScheme) {
    if (disabled) return colorScheme.disabledBg;
    switch (variant) {
      case Variant.primary: return colorScheme.primary;
      case Variant.secondary: return colorScheme.secondary;
      case Variant.tertiary: return Colors.transparent;
      case Variant.ghost: return Colors.transparent;
      case Variant.danger: return colorScheme.error;
    }
  }

  Color _textColor(ColorScheme colorScheme) {
    if (disabled) return colorScheme.disabledText;
    switch (variant) {
      case Variant.primary: return colorScheme.onPrimary;
      case Variant.danger: return colorScheme.onError;
      default: return colorScheme.primary;
    }
  }

  Border? _border(ColorScheme colorScheme) {
    if (variant == Variant.ghost || variant == Variant.tertiary) {
      return Border.all(color: colorScheme.outline, width: 1);
    }
    return null;
  }

  List<BoxShadow> _boxShadow(ColorScheme colorScheme) {
    return [
      BoxShadow(
        color: Colors.black.withOpacity(0.05),
        blurRadius: 2,
        offset: const Offset(0, 1),
      ),
    ];
  }

  Color _splashColor(ColorScheme colorScheme) {
    return _textColor(colorScheme).withOpacity(0.1);
  }

  Color _highlightColor(ColorScheme colorScheme) {
    return _textColor(colorScheme).withOpacity(0.05);
  }

  TextStyle get _textStyle => TextStyle(
    fontSize: _fontSize,
    fontWeight: FontWeight.w500,
    color: _textColor(Theme.of(context).colorScheme),
    letterSpacing: 0.25,
  );

  double get _cornerRadius => 6.0; // radiusMd

  double get _horizontalPadding {
    switch (size) {
      case Size.xs: return 8.0;  // space2
      case Size.sm: return 12.0; // space3
      case Size.md: return 16.0; // space4
      case Size.lg: return 20.0; // space5
      case Size.xl: return 24.0; // space6
    }
  }

  double get _verticalPadding {
    switch (size) {
      case Size.xs: return 4.0;  // space1
      case Size.sm: return 8.0;  // space2
      case Size.md: return 8.0;  // space2
      case Size.lg: return 12.0; // space3
      case Size.xl: return 12.0; // space3
    }
  }

  double get _minWidth {
    switch (size) {
      case Size.xs: return 32.0;
      case Size.sm: return 44.0;
      case Size.md: return 44.0;
      case Size.lg: return 48.0;
      case Size.xl: return 56.0;
    }
  }

  double get _minHeight {
    switch (size) {
      case Size.xs: return 28.0;
      case Size.sm: return 36.0;
      case Size.md: return 44.0;
      case Size.lg: return 48.0;
      case Size.xl: return 52.0;
    }
  }

  double get _fontSize {
    switch (size) {
      case Size.xs: return 12.0; // fontSizeXs
      case Size.sm: return 14.0; // fontSizeSm
      case Size.md: return 14.0; // fontSizeMd (buttons use smaller)
      case Size.lg: return 16.0; // fontSizeLg
      case Size.xl: return 18.0; // fontSizeXl
    }
  }

  double get _iconSpacing => 8.0; // space2

  double get _spinnerSize => 16.0;
}

enum Variant { primary, secondary, tertiary, ghost, danger }
enum Size { xs, sm, md, lg, xl }
enum IconAlignment { start, end }

// ColorScheme extension for design tokens
extension DesignTokens on ColorScheme {
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
}''',
        }

    def generate(self, spec: ComponentSpec, framework: str, output_dir: Path) -> List[Path]:
        """Generate component files from spec."""
        framework = framework.lower()
        if framework not in self.templates:
            raise ValueError(f"Unsupported framework: {framework}. Supported: {list(self.templates.keys())}")

        templates = self.templates[framework]
        output_files = []

        # Generate main component
        if framework in ['html']:
            # HTML: single file with embedded CSS
            content = self._render_html_component(spec, templates)
            output_path = output_dir / f"{spec.name.lower()}.html"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content, encoding='utf-8')
            output_files.append(output_path)

        elif framework in ['react']:
            # React: .tsx + .css
            tsx_content = self._render_react_component(spec, templates)
            css_content = self._render_react_css(spec, templates)

            output_dir.mkdir(parents=True, exist_ok=True)
            tsx_path = output_dir / f"{spec.name}.tsx"
            css_path = output_dir / f"{spec.name}.css"

            tsx_path.write_text(tsx_content, encoding='utf-8')
            css_path.write_text(css_content, encoding='utf-8')
            output_files.extend([tsx_path, css_path])

        elif framework in ['vue']:
            # Vue: single .vue file
            content = self._render_vue_component(spec, templates)
            output_path = output_dir / f"{spec.name}.vue"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content, encoding='utf-8')
            output_files.append(output_path)

        elif framework in ['swiftui']:
            # SwiftUI: single .swift file
            content = self._render_swiftui_component(spec, templates)
            output_path = output_dir / f"{spec.name}.swift"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content, encoding='utf-8')
            output_files.append(output_path)

        elif framework in ['flutter']:
            # Flutter: single .dart file
            content = self._render_flutter_component(spec, templates)
            output_path = output_dir / f"{spec.name.toLowerCase()}.dart"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content, encoding='utf-8')
            output_files.append(output_path)

        return output_files

    def _render_html_component(self, spec: ComponentSpec, templates: Dict[str, str]) -> str:
        """Render HTML component."""
        class_name = spec.name.lower().replace(' ', '-')
        accessibility_notes = self._generate_accessibility_notes(spec)

        variant_classes = ' '.join([f'{class_name}--variant-{v.lower()}' for v in spec.variants])
        size_classes = ' '.join([f'{class_name}--size-{s.lower()}' for s in spec.sizes])

        variant_styles = self._generate_variant_styles(class_name, spec.variants)
        size_styles = self._generate_size_styles(class_name, spec.sizes)

        template = templates['component']
        return Template(template).safe_substitute(
            name=spec.name,
            class_name=class_name,
            description=spec.description,
            accessibility_notes=accessibility_notes,
            variant_classes=variant_classes,
            size_classes=size_classes,
            variant_styles=variant_styles,
            size_styles=size_styles,
            children='<!-- Children -->',
            aria_attributes='',
            type='button',
            disabled_attr='',
            icon_before='',
            label=spec.name,
            icon_after='',
        )

    def _render_react_component(self, spec: ComponentSpec, templates: Dict[str, str]) -> str:
        """Render React TypeScript component."""
        accessibility_notes = self._generate_accessibility_notes(spec)

        variants_str = "', '".join(spec.variants) if spec.variants else "'primary'"
        sizes_str = "', '".join(spec.sizes) if spec.sizes else "'md'"

        extra_props = ''
        for prop in spec.props:
            required = '' if prop.get('required') else '?'
            extra_props += f"  /** {prop.get('description', '')} */\n  {prop['name']}{required}: {prop['type']};\n"

        template = templates['component']
        return Template(template).safe_substitute(
            name=spec.name,
            description=spec.description,
            accessibility_notes=accessibility_notes,
            variants=variants_str,
            sizes=sizes_str,
            extra_props=extra_props,
        )

    def _render_react_css(self, spec: ComponentSpec, templates: Dict[str, str]) -> str:
        """Render React CSS with token-based styling."""
        class_name = spec.name.lower()

        variant_styles = self._generate_variant_styles(class_name, spec.variants)
        size_styles = self._generate_size_styles(class_name, spec.sizes)

        template = templates.get('css', '')
        return Template(template).safe_substitute(
            name=class_name,
            variant_styles=variant_styles,
            size_styles=size_styles,
        )

    def _render_vue_component(self, spec: ComponentSpec, templates: Dict[str, str]) -> str:
        """Render Vue component."""
        accessibility_notes = self._generate_accessibility_notes(spec)

        variants_str = "', '".join(spec.variants) if spec.variants else "'primary'"
        sizes_str = "', '".join(spec.sizes) if spec.sizes else "'md'"

        extra_props = ''
        for prop in spec.props:
            required = '' if prop.get('required') else '?'
            extra_props += f"  {prop['name']}{required}: {prop['type']};\n"

        variant_styles = self._generate_variant_styles(spec.name.lower(), spec.variants)
        size_styles = self._generate_size_styles(spec.name.lower(), spec.sizes)

        template = templates['component']
        return Template(template).safe_substitute(
            name=spec.name,
            description=spec.description,
            accessibility_notes=accessibility_notes,
            variants=variants_str,
            sizes=sizes_str,
            extra_props=extra_props,
            variant_styles=variant_styles,
            size_styles=size_styles,
        )

    def _render_swiftui_component(self, spec: ComponentSpec, templates: Dict[str, str]) -> str:
        """Render SwiftUI component."""
        accessibility_notes = self._generate_accessibility_notes(spec)

        template = templates['component']
        return Template(template).safe_substitute(
            name=spec.name,
            description=spec.description,
            accessibility_notes=accessibility_notes,
        )

    def _render_flutter_component(self, spec: ComponentSpec, templates: Dict[str, str]) -> str:
        """Render Flutter component."""
        accessibility_notes = self._generate_accessibility_notes(spec)

        template = templates['component']
        return Template(template).safe_substitute(
            name=spec.name,
            description=spec.description,
            accessibility_notes=accessibility_notes,
        )

    def _generate_accessibility_notes(self, spec: ComponentSpec) -> str:
        """Generate accessibility documentation comments."""
        if not spec.accessibility:
            return ''

        notes = ['// Accessibility Notes:']
        for note in spec.accessibility:
            notes.append(f'// - {note}')
        return '\n'.join(notes) + '\n'

    def _generate_variant_styles(self, class_name: str, variants: List[str]) -> str:
        """Generate CSS for variants."""
        if not variants:
            return '/* No variants defined */'

        styles = []
        variant_colors = {
            'primary': ('var(--color-primary)', 'var(--color-primary-hover)', 'var(--color-primary-active)', 'var(--color-text-inverse)'),
            'secondary': ('var(--color-secondary)', 'var(--color-secondary-hover)', 'var(--color-secondary-active)', 'var(--color-text-inverse)'),
            'tertiary': ('transparent', 'var(--color-surface-hover)', 'var(--color-surface-hover)', 'var(--color-primary)'),
            'ghost': ('transparent', 'var(--color-surface-hover)', 'var(--color-surface-hover)', 'var(--color-text-primary)'),
            'danger': ('var(--color-error)', 'var(--color-error)', 'var(--color-error-text)', 'var(--color-text-inverse)'),
        }

        for variant in variants:
            bg, hover, active, text = variant_colors.get(variant.lower(), variant_colors['primary'])
            styles.append(f'''
.{class_name}--variant-{variant.lower()} {{
  background-color: {bg};
  color: {text};
}}
.{class_name}--variant-{variant.lower()}:hover:not(:disabled) {{
  background-color: {hover};
}}
.{class_name}--variant-{variant.lower()}:active:not(:disabled) {{
  background-color: {active};
}}''')

        return '\n'.join(styles)

    def _generate_size_styles(self, class_name: str, sizes: List[str]) -> str:
        """Generate CSS for sizes."""
        if not sizes:
            return '/* No sizes defined */'

        size_map = {
            'xs': ('var(--space-1)', 'var(--space-2)', 'var(--font-size-xs)', '28px'),
            'sm': ('var(--space-2)', 'var(--space-3)', 'var(--font-size-sm)', '36px'),
            'md': ('var(--space-2)', 'var(--space-4)', 'var(--font-size-sm)', '44px'),
            'lg': ('var(--space-3)', 'var(--space-5)', 'var(--font-size-md)', '48px'),
            'xl': ('var(--space-3)', 'var(--space-6)', 'var(--font-size-lg)', '52px'),
        }

        styles = []
        for size in sizes:
            v_pad, h_pad, font_size, min_height = size_map.get(size.lower(), size_map['md'])
            styles.append(f'''
.{class_name}--size-{size.lower()} {{
  padding: {v_pad} {h_pad};
  font-size: {font_size};
  min-height: {min_height};
}}''')

        return '\n'.join(styles)


def load_spec_from_file(spec_path: Path) -> ComponentSpec:
    """Load component spec from markdown file."""
    content = spec_path.read_text(encoding='utf-8')

    # Parse frontmatter and sections (simplified)
    spec = ComponentSpec(
        name=spec_path.stem.replace('-', '').replace('_', '').title(),
        description=f"Auto-generated from {spec_path.name}",
    )

    # Extract props from markdown tables
    prop_pattern = r'\|\s*(\w+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|'
    for match in re.finditer(prop_pattern, content):
        prop_name, prop_type, prop_default, prop_desc = match.groups()
        if prop_name.lower() not in ['prop', 'name', 'property']:
            spec.props.append({
                'name': prop_name.strip(),
                'type': prop_type.strip(),
                'default': prop_default.strip(),
                'description': prop_desc.strip(),
                'required': 'required' in prop_default.lower(),
            })

    # Default variants/sizes if not specified
    if not spec.variants:
        spec.variants = ['primary', 'secondary', 'tertiary', 'ghost', 'danger']
    if not spec.sizes:
        spec.sizes = ['xs', 'sm', 'md', 'lg', 'xl']
    if not spec.states:
        spec.states = ['default', 'hover', 'active', 'focus', 'disabled', 'loading']

    # Default accessibility
    spec.accessibility = [
        'Keyboard focusable with visible focus ring',
        'ARIA labels for icon-only variants',
        'Disabled state announced to screen readers',
        'Loading state with aria-busy',
        'Meets 44x44px minimum touch target',
    ]

    return spec


def main():
    parser = argparse.ArgumentParser(
        description="Generate accessible, token-compliant components from specifications",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate-component.py --spec component-spec.md --framework react --output ./src/components
  python generate-component.py --spec page-spec.md --framework html --output ./components
  python generate-component.py --interactive --framework vue
        """
    )

    parser.add_argument('--spec', '-s', help='Component specification file (markdown)')
    parser.add_argument('--framework', '-f', required=True,
                       choices=['html', 'react', 'vue', 'swiftui', 'flutter'],
                       help='Target framework')
    parser.add_argument('--output', '-o', required=True, help='Output directory')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    parser.add_argument('--name', '-n', help='Component name (for interactive mode)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    generator = ComponentGenerator()
    output_dir = Path(args.output)

    if args.interactive:
        # Interactive mode
        name = args.name or input("Component name (e.g., PrimaryButton): ").strip()
        if not name:
            print("Error: Component name required", file=sys.stderr)
            sys.exit(1)

        description = input("Description: ").strip()
        variants = input("Variants (comma-separated, default: primary,secondary,tertiary,ghost,danger): ").strip()
        sizes = input("Sizes (comma-separated, default: xs,sm,md,lg,xl): ").strip()

        spec = ComponentSpec(
            name=name,
            description=description or f"{name} component",
            variants=[v.strip() for v in variants.split(',')] if variants else ['primary', 'secondary', 'tertiary', 'ghost', 'danger'],
            sizes=[s.strip() for s in sizes.split(',')] if sizes else ['xs', 'sm', 'md', 'lg', 'xl'],
        )
    else:
        if not args.spec:
            print("Error: --spec required in non-interactive mode", file=sys.stderr)
            sys.exit(1)

        spec_path = Path(args.spec)
        if not spec_path.exists():
            print(f"Error: Spec file not found: {spec_path}", file=sys.stderr)
            sys.exit(1)

        if args.verbose:
            print(f"Loading spec from: {spec_path}")
        spec = load_spec_from_file(spec_path)

    if args.verbose:
        print(f"Generating {args.framework} component: {spec.name}")

    output_files = generator.generate(spec, args.framework, output_dir)

    print(f"\n[OK] Generated {len(output_files)} file(s):")
    for f in output_files:
        print(f"   {f}")

    if args.verbose:
        print(f"\n[LIST] Spec used:")
        print(f"   Name: {spec.name}")
        print(f"   Variants: {spec.variants}")
        print(f"   Sizes: {spec.sizes}")
        print(f"   Props: {len(spec.props)}")


if __name__ == '__main__':
    main()