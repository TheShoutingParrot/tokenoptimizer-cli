# Token Optimizer

A command-line tool for optimizing tokens using [The Token Company](https://thetokencompany.com) API.

I created this (mostly with vibes (TM)) to help my agents (claude / codex) to interface with the token company when developping.

Quickly hacked together with vibes.

## Installation

### Quick Install (Recommended)

```bash
curl -sSL https://raw.githubusercontent.com/yourusername/tokenoptimizer/main/install.sh | bash
```

Or download and run manually:

```bash
wget https://raw.githubusercontent.com/yourusername/tokenoptimizer/main/install.sh
chmod +x install.sh
./install.sh
```

On my system for some reason the above script requires the "--break-system-packages" flag. If you get the same error that tells the user to use this flag, just append it when running install.sh like so: `./install.sh --break-system-packages`.


### Using pip

```bash
pip install tokenoptimizer
```

### From Source

```bash
git clone https://github.com/yourusername/tokenoptimizer.git
cd tokenoptimizer
pip install -e .
```

## Authentication

Get your API key from [The Token Company](https://thetokencompany.com).

### Set your API key

```bash
# Interactive prompt
tokenoptimizer auth set

# Or provide directly
tokenoptimizer auth set --key YOUR_API_KEY

# Or use environment variable
export TOKENOPTIMIZER_API_KEY="YOUR_API_KEY"
```

### Manage authentication

```bash
tokenoptimizer auth show     # Show current API key status
tokenoptimizer auth delete   # Remove stored API key
tokenoptimizer auth path     # Show config file path
```

## Usage

### Basic Usage

```bash
# From command line arguments
tokenoptimizer "Your long prompt that needs optimization"

# From stdin (pipe)
echo "Your prompt" | tokenoptimizer

# From a file
tokenoptimizer --file prompt.txt
cat prompt.txt | tokenoptimizer
```

### Prompt for using with Claude or Codex

I use this prompt:

```
Use tokenoptimizer to compress prompts while preserving meaning. Use it like so: `echo "X" | tokenoptimizer`. Adjust aggressiveness as needed with `-a` flag. Do not read the output at all and do not assess it.
```

### Aggressiveness Levels

Control how aggressively the optimizer compresses your text:

```bash
# Preset levels
tokenoptimizer --light "Your prompt"       # 0.2 - Preserves content safely
tokenoptimizer --moderate "Your prompt"    # 0.5 - Balanced (default)
tokenoptimizer --aggressive "Your prompt"  # 0.8 - Maximum reduction

# Custom level (0.0 to 1.0)
tokenoptimizer -a 0.7 "Your prompt"
tokenoptimizer --aggressiveness 0.3 "Your prompt"
```

| Level | Value | Description |
|-------|-------|-------------|
| Light | 0.1-0.3 | Preserves content safely |
| Moderate | 0.4-0.6 | Balances compression with quality |
| Aggressive | 0.7-0.9 | Maximizes token reduction |

### Token Limits

```bash
# Set maximum output tokens
tokenoptimizer --max-tokens 100 "Your prompt"

# Set minimum output tokens
tokenoptimizer --min-tokens 50 "Your prompt"
```

### Output Options

```bash
# Quiet mode - only output the optimized text
tokenoptimizer -q "Your prompt"
tokenoptimizer --quiet "Your prompt"

# Stats only - show statistics without the optimized text
tokenoptimizer -s "Your prompt"
tokenoptimizer --stats-only "Your prompt"
```

### All Options

```
tokenoptimizer [OPTIONS] [PROMPT]

Options:
  --version              Show version
  -f, --file FILE        Read prompt from file
  -a, --aggressiveness   Compression level 0.0-1.0 (default: 0.5)
  -l, --light            Light compression (0.2)
  -m, --moderate         Moderate compression (0.5)
  -A, --aggressive       Aggressive compression (0.8)
  --max-tokens N         Maximum output tokens
  --min-tokens N         Minimum output tokens
  -q, --quiet            Suppress statistics
  -s, --stats-only       Only show statistics
  --timeout SECONDS      Request timeout (default: 60)
  -h, --help             Show help message

Commands:
  auth set [--key KEY]   Set API key
  auth show              Show API key status
  auth delete            Delete stored API key
  auth path              Show config file path
```

## Examples

### Optimize a System Prompt

```bash
tokenoptimizer "You are a helpful AI assistant. Your goal is to help users
with their questions and tasks. Be concise, accurate, and friendly. Always
provide clear explanations and examples when appropriate."
```

### Batch Processing

```bash
# Process multiple files
for file in prompts/*.txt; do
    tokenoptimizer --file "$file" > "optimized/$(basename $file)"
done
```

### Integration with Other Tools

```bash
# Use with jq for JSON prompts
cat data.json | jq -r '.prompt' | tokenoptimizer

# Combine with clipboard (macOS)
pbpaste | tokenoptimizer | pbcopy

# Combine with clipboard (Linux with xclip)
xclip -o | tokenoptimizer | xclip -selection clipboard
```

### In Scripts

```bash
#!/bin/bash
ORIGINAL_PROMPT="Your very long prompt here..."
OPTIMIZED=$(echo "$ORIGINAL_PROMPT" | tokenoptimizer -q)
echo "Optimized prompt: $OPTIMIZED"
```

## Configuration

### Config File Location

```
~/.config/tokenoptimizer/config
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `TOKENOPTIMIZER_API_KEY` | API key (overrides config file) |

## Development

### Setup Development Environment

```bash
git clone https://github.com/yourusername/tokenoptimizer.git
cd tokenoptimizer
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
pytest --cov=tokenoptimizer
```

### Code Formatting

```bash
black tokenoptimizer/
ruff check tokenoptimizer/
```

## License

BSD 3-Clause License - see [LICENSE](LICENSE) file for details.

Copyright (c) 2025, Vinor Ltd

## Support

- [The Token Company Documentation](https://thetokencompany.com/docs)
