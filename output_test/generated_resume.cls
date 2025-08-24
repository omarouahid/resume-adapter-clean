
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{resume}[2024/01/01 Resume class]

\LoadClass[11pt,letterpaper]{article}

\usepackage[parfill]{parskip}
\usepackage{array}
\usepackage{ifthen}
\usepackage{geometry}
\usepackage{enumitem}

% Define colors
\usepackage{xcolor}
\definecolor{primary}{RGB}{0, 0, 0}
\definecolor{secondary}{RGB}{100, 100, 100}

% Remove page numbers
\pagestyle{empty}

% Name command
\def \name#1{\def\@name{#1}}
\def \@name {}

% Contact command  
\def \contact#1{\def\@contact{#1}}
\def \@contact {}

% Make header
\def \makeheader {
  \begin{center}
    {\Huge \scshape \@name}
    \vspace{0.1in}
    
    \ifthenelse{\equal{\@contact}{}}{}{
      \\
      \@contact
    }
  \end{center}
  \vspace{0.2in}
}

% Section command
\renewcommand{\section}[1]{
  \vspace{0.1in}
  {\Large \scshape #1}
  \vspace{0.05in}
  \hrule
  \vspace{0.1in}
}

% Resume item command
\newcommand{\resumeItem}[3]{
  \vspace{0.05in}
  \begin{tabular*}{\textwidth}{l@{\extracolsep{\fill}}r}
    \textbf{#1} & #3 \\
    \textit{#2} & \\
  \end{tabular*}
  \vspace{-0.1in}
}

% Resume skills command
\newcommand{\resumeSkills}[1]{
  \begin{itemize}[leftmargin=0.1in, label={}]
    \item #1
  \end{itemize}
}

% Custom itemize
\renewenvironment{itemize}{
  \begin{list}{$\cdot$}{
    \setlength{\itemsep}{0pt}
    \setlength{\parsep}{0pt}
    \setlength{\topsep}{0pt}
    \setlength{\partopsep}{0pt}
    \setlength{\leftmargin}{0.2in}
  }
}{
  \end{list}
}
