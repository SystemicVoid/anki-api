# MathJax Notation for Anki Cards

Practical quick reference for mathematical notation in flashcards. Works in both Anki Desktop and the web UI.

## Critical: Delimiters

**Anki uses different delimiters than standard LaTeX:**

| Type | Anki MathJax | NOT this |
|------|--------------|----------|
| Inline | `\( ... \)` | `$ ... $` |
| Display | `\[ ... \]` | `$$ ... $$` |

```
Inline example: The dot product \(\mathbf{v} \cdot \mathbf{w}\) measures alignment.

Display example:
\[
\begin{bmatrix} a & b \\ c & d \end{bmatrix}
\]
```

## Linear Algebra Notation

### Vectors

| Element | MathJax | Renders |
|---------|---------|---------|
| Bold vector | `\mathbf{v}` | **v** |
| Vector with arrow | `\vec{v}` | v⃗ |
| Vector norm | `\|\mathbf{v}\|` | ‖**v**‖ |
| Dot product | `\mathbf{v} \cdot \mathbf{w}` | **v** · **w** |
| Cross product | `\mathbf{v} \times \mathbf{w}` | **v** × **w** |

### Unit Vectors and Basis Vectors

| Element | MathJax | Note |
|---------|---------|------|
| General unit vector | `\hat{\mathbf{u}}` | Bold u with hat |
| i-hat (basis) | `\hat{\imath}` | Dotless i with hat |
| j-hat (basis) | `\hat{\jmath}` | Dotless j with hat |
| k-hat (basis) | `\hat{k}` | Regular k with hat |

**WARNING - LaTeX vs MathJax difference:**
```
BROKEN:  \hat{\textbf{\i}}     -- \textbf{\i} is LaTeX-only
WORKS:   \hat{\imath}          -- MathJax dotless i
```

### Matrices

```
Row vector (1x2):
\begin{bmatrix} a & b \end{bmatrix}

Column vector (2x1):
\begin{bmatrix} x \\ y \end{bmatrix}

2x2 matrix:
\begin{bmatrix} a & b \\ c & d \end{bmatrix}

3x3 matrix:
\begin{bmatrix}
a & b & c \\
d & e & f \\
g & h & i
\end{bmatrix}
```

Matrix types:
- `bmatrix` - square brackets [ ]
- `pmatrix` - parentheses ( )
- `vmatrix` - vertical bars | | (determinant)
- `matrix` - no delimiters

### Spaces and Sets

| Element | MathJax | Renders |
|---------|---------|---------|
| Real numbers | `\mathbb{R}` | ℝ |
| n-dimensional | `\mathbb{R}^n` | ℝⁿ |
| 2D to 1D map | `\mathbb{R}^2 \to \mathbb{R}` | ℝ² → ℝ |
| Element of | `x \in \mathbb{R}` | x ∈ ℝ |

## Common Symbols

### Greek Letters
```
\alpha \beta \gamma \delta \epsilon \theta \lambda \mu \pi \sigma \phi \omega
\Gamma \Delta \Theta \Lambda \Pi \Sigma \Phi \Omega
```

### Operations
```
\cdot      centered dot (multiplication)
\times     cross/times
\div       division
\pm        plus-minus
\sum       summation
\prod      product
\int       integral
```

### Relations
```
\eq \neq \lt \gt \le \ge \approx \equiv
\subset \supset \in \notin
\to \mapsto \implies \iff
```

### Decorations
```
\hat{x}      x with hat
\bar{x}      x with bar
\dot{x}      x with dot (derivative)
\ddot{x}     x with double dot
\tilde{x}    x with tilde
\overline{xyz}   overline spanning multiple chars
```

## JSON Escaping

When writing MathJax in JSON (for card generation), backslashes must be doubled:

```json
{
  "front": "What is \\(\\mathbf{v} \\cdot \\mathbf{w}\\)?",
  "back": "The matrix is \\(\\begin{bmatrix} a & b \\end{bmatrix}\\)"
}
```

## Quick Reference Card

```
Vectors:        \mathbf{v}, \vec{v}
Unit vectors:   \hat{\mathbf{u}}
Basis vectors:  \hat{\imath}, \hat{\jmath}, \hat{k}
Matrices:       \begin{bmatrix} a & b \\ c & d \end{bmatrix}
Norm:           \|\mathbf{v}\|
Dot product:    \mathbf{v} \cdot \mathbf{w}
Real space:     \mathbb{R}^n
Inline:         \( ... \)
Display:        \[ ... \]
```
