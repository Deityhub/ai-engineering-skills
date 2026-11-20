#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract Design Tokens from Project Files

Parses CSS custom properties, Tailwind config, Figma Tokens JSON, and Style Dictionary
formats into a canonical token format for use across the design skill.

Usage:
    python extract-tokens.py --input ./my-project --output tokens.json
    python extract-tokens.py --input ./styles --format css --output tokens.css
    python extract-tokens.py --input ./tailwind.config.js --format json --output tokens.json
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import cssutils
import yaml

# Silence cssutils warnings
cssutils.log.setLevel('ERROR')


class TokenExtractor:
    """Extract design tokens from various source formats."""

    def __init__(self):
        self.tokens = {
            "spacing": {},
            "color": {},
            "typography": {
                "fontFamily": {},
                "fontSize": {},
                "fontWeight": {},
                "lineHeight": {},
                "letterSpacing": {}
            },
            "borderRadius": {},
            "shadow": {},
            "breakpoints": {},
            "zIndex": {},
            "transition": {}
        }
        self.errors = []
        self.warnings = []

    def extract_from_css(self, css_content: str, source: str) -> Dict:
        """Extract CSS custom properties from CSS content."""
        sheet = cssutils.parseString(css_content)
        self._parse_css_rules(sheet.cssRules, source)
        return self.tokens

    def extract_from_css_file(self, file_path: Path) -> Dict:
        """Extract tokens from a CSS file."""
        try:
            content = file_path.read_text(encoding='utf-8')
            return self.extract_from_css(content, str(file_path))
        except Exception as e:
            self.errors.append(f"Failed to parse {file_path}: {e}")
            return self.tokens

    def _parse_css_rules(self, rules, source: str):
        """Recursively parse CSS rules for custom properties."""
        for rule in rules:
            if rule.type == rule.STYLE_RULE:
                self._extract_custom_properties(rule.style, source)
            elif rule.type == rule.MEDIA_RULE:
                self._parse_css_rules(rule.cssRules, source)
            elif rule.type == rule.SUPPORTS_RULE:
                self._parse_css_rules(rule.cssRules, source)

    def _extract_custom_properties(self, style, source: str):
        """Extract --custom-properties from a style declaration."""
        for prop in style:
            if prop.name.startswith('--'):
                name = prop.name[2:]  # Remove --
                value = prop.value.strip()
                self._categorize_token(name, value, source)

    def _categorize_token(self, name: str, value: str, source: str):
        """Categorize a token by its name pattern."""
        # Spacing: --space-*, --spacing-*
        if re.match(r'^(space|spacing)-', name):
            key = name.replace('spacing-', '').replace('space-', '')
            self.tokens["spacing"][key] = {"value": value, "source": source, "type": "dimension"}

        # Color: --color-*, --colors-*
        elif re.match(r'^(color|colors)-', name):
            # Parse nested structure: color-primary-hover -> color.primary.hover
            parts = name.replace('colors-', '').replace('color-', '').split('-')
            self._set_nested_color(parts, value, source)

        # Typography: --font-*, --typography-*
        elif re.match(r'^(font|typography)-', name):
            parts = name.replace('typography-', '').replace('font-', '').split('-')
            self._set_nested_typography(parts, value, source)

        # Border radius: --radius-*, --border-radius-*
        elif re.match(r'^(radius|border-radius)-', name):
            key = name.replace('border-radius-', '').replace('radius-', '')
            self.tokens["borderRadius"][key] = {"value": value, "source": source, "type": "dimension"}

        # Shadows: --shadow-*, --box-shadow-*
        elif re.match(r'^(shadow|box-shadow)-', name):
            key = name.replace('box-shadow-', '').replace('shadow-', '')
            self.tokens["shadow"][key] = {"value": value, "source": source, "type": "shadow"}

        # Breakpoints: --bp-*, --breakpoint-*
        elif re.match(r'^(bp|breakpoint)-', name):
            key = name.replace('breakpoint-', '').replace('bp-', '')
            self.tokens["breakpoints"][key] = {"value": value, "source": source, "type": "dimension"}

        # Z-index: --z-*, --z-index-*
        elif re.match(r'^(z|z-index)-', name):
            key = name.replace('z-index-', '').replace('z-', '')
            try:
                self.tokens["zIndex"][key] = {"value": int(value), "source": source, "type": "number"}
            except ValueError:
                self.tokens["zIndex"][key] = {"value": value, "source": source, "type": "number"}

        # Transitions: --transition-*, --animation-*
        elif re.match(r'^(transition|animation)-', name):
            key = name.replace('animation-', '').replace('transition-', '')
            self.tokens["transition"][key] = {"value": value, "source": source, "type": "transition"}

    def _set_nested_color(self, parts: List[str], value: str, source: str):
        """Set nested color token (e.g., primary-hover -> color.primary.hover)."""
        if len(parts) < 2:
            return

        category = parts[0]
        prop = parts[1]
        state = parts[2] if len(parts) > 2 else "value"

        if category not in self.tokens["color"]:
            self.tokens["color"][category] = {"type": "color"}

        if state not in self.tokens["color"][category]:
            self.tokens["color"][category][state] = {}

        # Handle light/dark variants in value
        self.tokens["color"][category][state] = {
            "value": value,
            "source": source
        }

    def _set_nested_typography(self, parts: List[str], value: str, source: str):
        """Set nested typography token."""
        if len(parts) < 2:
            return

        category = parts[0]
        key = '-'.join(parts[1:])

        if category not in self.tokens["typography"]:
            self.tokens["typography"][category] = {}

        self.tokens["typography"][category][key] = {"value": value, "source": source}

    def extract_from_tailwind(self, config_path: Path) -> Dict:
        """Extract tokens from Tailwind config (JS/TS/JSON)."""
        try:
            content = config_path.read_text(encoding='utf-8')

            # Try to parse as JSON first
            if config_path.suffix == '.json':
                config = json.loads(content)
            else:
                # Extract JavaScript object - simplified parser
                config = self._parse_tailwind_js(content)

            self._process_tailwind_config(config, str(config_path))
            return self.tokens
        except Exception as e:
            self.errors.append(f"Failed to parse Tailwind config {config_path}: {e}")
            return self.tokens

    def _parse_tailwind_js(self, content: str) -> Dict:
        """Simple Tailwind JS config parser (handles common patterns)."""
        # Remove comments
        content = re.sub(r'//.*', '', content)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

        # Find module.exports or export default
        match = re.search(r'(?:module\.exports|export\s+default)\s*=\s*(\{[\s\S]*\})', content)
        if not match:
            return {}

        obj_str = match.group(1)

        # Convert JS object to JSON-like (simplified)
        obj_str = re.sub(r'(\w+):', r'"\1":', obj_str)  # Quote keys
        obj_str = re.sub(r',\s*}', '}', obj_str)  # Trailing commas
        obj_str = re.sub(r',\s*]', ']', obj_str)

        try:
            return json.loads(obj_str)
        except json.JSONDecodeError:
            # Fallback: return empty
            return {}

    def _process_tailwind_config(self, config: Dict, source: str):
        """Process Tailwind theme config into tokens."""
        theme = config.get('theme', {})
        extend = theme.get('extend', {})

        # Merge theme and extend
        for key in ['spacing', 'colors', 'fontSize', 'fontFamily', 'fontWeight',
                    'lineHeight', 'letterSpacing', 'borderRadius', 'boxShadow',
                    'screens', 'zIndex', 'transitionDuration', 'transitionTimingFunction']:
            theme_val = theme.get(key, {})
            extend_val = extend.get(key, {})
            merged = {**theme_val, **extend_val}

            if merged:
                self._map_tailwind_category(key, merged, source)

    def _map_tailwind_category(self, category: str, values: Dict, source: str):
        """Map Tailwind categories to our token structure."""
        if category == 'spacing':
            for key, value in values.items():
                self.tokens["spacing"][str(key)] = {"value": f"{value}rem" if isinstance(value, (int, float)) else str(value), "source": source, "type": "dimension"}

        elif category == 'colors':
            for color_name, shades in values.items():
                if isinstance(shades, dict):
                    for shade, value in shades.items():
                        if shade == 'DEFAULT':
                            self.tokens["color"].setdefault(color_name, {"type": "color"})["value"] = {"value": value, "source": source}
                        else:
                            self.tokens["color"].setdefault(color_name, {"type": "color"})[shade] = {"value": value, "source": source}
                else:
                    self.tokens["color"].setdefault(color_name, {"type": "color"})["value"] = {"value": shades, "source": source}

        elif category == 'fontSize':
            for key, value in values.items():
                if isinstance(value, list):
                    size, line_height = value[0], value[1] if len(value) > 1 else None
                    self.tokens["typography"]["fontSize"][str(key)] = {"value": size, "source": source, "type": "fontSize"}
                    if line_height:
                        self.tokens["typography"]["lineHeight"][str(key)] = {"value": str(line_height), "source": source}
                else:
                    self.tokens["typography"]["fontSize"][str(key)] = {"value": value, "source": source, "type": "fontSize"}

        elif category == 'fontFamily':
            for key, value in values.items():
                fonts = value if isinstance(value, list) else [value]
                self.tokens["typography"]["fontFamily"][str(key)] = {"value": ', '.join(fonts), "source": source, "type": "fontFamily"}

        elif category == 'fontWeight':
            for key, value in values.items():
                self.tokens["typography"]["fontWeight"][str(key)] = {"value": str(value), "source": source, "type": "fontWeight"}

        elif category == 'lineHeight':
            for key, value in values.items():
                self.tokens["typography"]["lineHeight"][str(key)] = {"value": str(value), "source": source, "type": "lineHeight"}

        elif category == 'letterSpacing':
            for key, value in values.items():
                self.tokens["typography"]["letterSpacing"][str(key)] = {"value": str(value), "source": source, "type": "letterSpacing"}

        elif category == 'borderRadius':
            for key, value in values.items():
                self.tokens["borderRadius"][str(key)] = {"value": f"{value}rem" if isinstance(value, (int, float)) else str(value), "source": source, "type": "dimension"}

        elif category == 'boxShadow':
            for key, value in values.items():
                self.tokens["shadow"][str(key)] = {"value": value, "source": source, "type": "shadow"}

        elif category == 'screens':
            for key, value in values.items():
                self.tokens["breakpoints"][str(key)] = {"value": f"{value}px" if isinstance(value, (int, float)) else str(value), "source": source, "type": "dimension"}

        elif category == 'zIndex':
            for key, value in values.items():
                self.tokens["zIndex"][str(key)] = {"value": value, "source": source, "type": "number"}

        elif category in ['transitionDuration', 'transitionTimingFunction']:
            for key, value in values.items():
                self.tokens["transition"][str(key)] = {"value": str(value), "source": source, "type": "transition"}

    def extract_from_figma_json(self, json_path: Path) -> Dict:
        """Extract tokens from Figma Tokens JSON (Style Dictionary format)."""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self._process_figma_tokens(data, str(json_path))
            return self.tokens
        except Exception as e:
            self.errors.append(f"Failed to parse Figma JSON {json_path}: {e}")
            return self.tokens

    def _process_figma_tokens(self, data: Dict, source: str):
        """Process Figma Tokens / Style Dictionary format."""
        # Handle both flat and nested structures
        def process_group(group: Dict, path: List[str] = []):
            for key, value in group.items():
                if isinstance(value, dict) and 'value' in value:
                    # This is a token
                    token_type = value.get('type', 'unknown')
                    full_path = path + [key]
                    self._assign_figma_token(full_path, value, token_type, source)
                elif isinstance(value, dict):
                    # Nested group
                    process_group(value, path + [key])

        process_group(data)

    def _assign_figma_token(self, path: List[str], token: Dict, token_type: str, source: str):
        """Assign a Figma token to our structure."""
        if not path:
            return

        category = path[0].lower()
        token_name = '-'.join(path[1:]) if len(path) > 1 else path[0]
        value = token['value']

        if category in ['spacing', 'space']:
            self.tokens["spacing"][token_name] = {"value": value, "source": source, "type": "dimension"}

        elif category in ['color', 'colors']:
            # Path: color/primary/value or color/primary/hover
            if len(path) >= 3:
                color_name = path[1]
                state = path[2]
                self.tokens["color"].setdefault(color_name, {"type": "color"})[state] = {"value": value, "source": source}
            else:
                self.tokens["color"].setdefault(token_name, {"type": "color"})["value"] = {"value": value, "source": source}

        elif category in ['typography', 'font', 'type']:
            # Path: typography/fontSize/body or typography/fontWeight/bold
            if len(path) >= 3:
                subcat = path[1]
                key = path[2]
                if subcat not in self.tokens["typography"]:
                    self.tokens["typography"][subcat] = {}
                self.tokens["typography"][subcat][key] = {"value": value, "source": source}

        elif category in ['borderradius', 'radius']:
            self.tokens["borderRadius"][token_name] = {"value": value, "source": source, "type": "dimension"}

        elif category in ['shadow', 'boxshadow']:
            self.tokens["shadow"][token_name] = {"value": value, "source": source, "type": "shadow"}

        elif category in ['breakpoint', 'breakpoints', 'screen', 'screens']:
            self.tokens["breakpoints"][token_name] = {"value": value, "source": source, "type": "dimension"}

        elif category in ['zindex', 'z-index']:
            self.tokens["zIndex"][token_name] = {"value": value, "source": source, "type": "number"}

        elif category in ['transition', 'animation']:
            self.tokens["transition"][token_name] = {"value": value, "source": source, "type": "transition"}

    def extract_from_directory(self, dir_path: Path, patterns: List[str] = None) -> Dict:
        """Extract tokens from all supported files in a directory."""
        if patterns is None:
            patterns = [
                '**/*.css', '**/*.scss', '**/*.sass',
                '**/tailwind.config.*', '**/tailwind.*.js',
                '**/figma-tokens.json', '**/tokens.json',
                '**/style-dictionary.json', '**/design-tokens.json'
            ]

        for pattern in patterns:
            for file_path in dir_path.glob(pattern):
                if file_path.is_file():
                    if file_path.suffix in ['.css', '.scss', '.sass']:
                        self.extract_from_css_file(file_path)
                    elif 'tailwind' in file_path.name:
                        self.extract_from_tailwind(file_path)
                    elif file_path.suffix == '.json':
                        self.extract_from_figma_json(file_path)

        return self.tokens

    def to_json(self, pretty: bool = True) -> str:
        """Export tokens as JSON."""
        # Clean up empty categories
        cleaned = {k: v for k, v in self.tokens.items() if v}
        indent = 2 if pretty else None
        return json.dumps(cleaned, indent=indent)

    def to_css(self) -> str:
        """Export tokens as CSS custom properties."""
        lines = [":root {"]

        # Spacing
        if self.tokens["spacing"]:
            lines.append("  /* Spacing */")
            for key, token in sorted(self.tokens["spacing"].items()):
                lines.append(f"  --space-{key}: {token['value']};")

        # Color
        if self.tokens["color"]:
            lines.append("\n  /* Color */")
            for category, states in self.tokens["color"].items():
                for state, token in states.items():
                    if isinstance(token, dict) and 'value' in token:
                        name = f"{category}-{state}" if state != 'value' else category
                        lines.append(f"  --color-{name}: {token['value']};")
                    elif isinstance(token, str):
                        lines.append(f"  --color-{category}: {token};")

        # Typography
        if self.tokens["typography"]:
            lines.append("\n  /* Typography */")
            for subcat, values in self.tokens["typography"].items():
                if isinstance(values, dict):
                    for key, token in values.items():
                        if isinstance(token, dict) and 'value' in token:
                            lines.append(f"  --font-{subcat}-{key}: {token['value']};")
                        elif isinstance(token, str):
                            lines.append(f"  --font-{subcat}-{key}: {token};")

        # Border radius
        if self.tokens["borderRadius"]:
            lines.append("\n  /* Border Radius */")
            for key, token in sorted(self.tokens["borderRadius"].items()):
                lines.append(f"  --radius-{key}: {token['value']};")

        # Shadows
        if self.tokens["shadow"]:
            lines.append("\n  /* Shadows */")
            for key, token in sorted(self.tokens["shadow"].items()):
                lines.append(f"  --shadow-{key}: {token['value']};")

        # Breakpoints
        if self.tokens["breakpoints"]:
            lines.append("\n  /* Breakpoints */")
            for key, token in sorted(self.tokens["breakpoints"].items()):
                lines.append(f"  --bp-{key}: {token['value']};")

        # Z-index
        if self.tokens["zIndex"]:
            lines.append("\n  /* Z-Index */")
            for key, token in sorted(self.tokens["zIndex"].items()):
                lines.append(f"  --z-{key}: {token['value']};")

        # Transitions
        if self.tokens["transition"]:
            lines.append("\n  /* Transitions */")
            for key, token in sorted(self.tokens["transition"].items()):
                lines.append(f"  --transition-{key}: {token['value']};")

        lines.append("}")
        return "\n".join(lines)

    def get_summary(self) -> Dict:
        """Get summary of extracted tokens."""
        return {
            "categories": {k: len(v) for k, v in self.tokens.items() if v},
            "total_tokens": sum(len(v) for v in self.tokens.values() if v),
            "errors": self.errors,
            "warnings": self.warnings
        }


def main():
    parser = argparse.ArgumentParser(
        description="Extract design tokens from project files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python extract-tokens.py --input ./my-project --output tokens.json
  python extract-tokens.py --input ./styles --format css --output tokens.css
  python extract-tokens.py --input ./tailwind.config.js --format json --output tokens.json
  python extract-tokens.py --input ./figma-tokens.json --format json --output tokens.json
        """
    )

    parser.add_argument('--input', '-i', required=True, help='Input file or directory')
    parser.add_argument('--output', '-o', required=True, help='Output file path')
    parser.add_argument('--format', '-f', choices=['json', 'css'], default='json', help='Output format')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"Error: Input path does not exist: {input_path}", file=sys.stderr)
        sys.exit(1)

    extractor = TokenExtractor()

    if input_path.is_dir():
        if args.verbose:
            print(f"Scanning directory: {input_path}")
        extractor.extract_from_directory(input_path)
    else:
        if args.verbose:
            print(f"Processing file: {input_path}")

        if input_path.suffix in ['.css', '.scss', '.sass']:
            extractor.extract_from_css_file(input_path)
        elif 'tailwind' in input_path.name:
            extractor.extract_from_tailwind(input_path)
        elif input_path.suffix == '.json':
            extractor.extract_from_figma_json(input_path)
        else:
            print(f"Error: Unsupported file type: {input_path.suffix}", file=sys.stderr)
            sys.exit(1)

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.format == 'json':
        output_path.write_text(extractor.to_json(), encoding='utf-8')
    elif args.format == 'css':
        output_path.write_text(extractor.to_css(), encoding='utf-8')

    # Print summary
    summary = extractor.get_summary()
    print(f"\n[OK] Extraction complete!")
    print(f"   Output: {output_path}")
    print(f"   Categories: {summary['categories']}")
    print(f"   Total tokens: {summary['total_tokens']}")

    if extractor.errors:
        print(f"\n[WARN]  Errors ({len(extractor.errors)}):")
        for error in extractor.errors:
            print(f"   - {error}")

    if extractor.warnings:
        print(f"\n[WARN]  Warnings ({len(extractor.warnings)}):")
        for warning in extractor.warnings:
            print(f"   - {warning}")

    if args.verbose and summary['total_tokens'] > 0:
        print(f"\n[LIST] Token categories found:")
        for cat, count in summary['categories'].items():
            print(f"   {cat}: {count} tokens")


if __name__ == '__main__':
    main()