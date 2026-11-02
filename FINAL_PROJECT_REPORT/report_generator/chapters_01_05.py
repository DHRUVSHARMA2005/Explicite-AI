"""Chapters 1–5: Introduction, Objectives, Literature Review, Existing Systems, Architecture."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from styles import *
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH


def build_chapters_01_05(doc):
    _ch1_introduction(doc)
    page_break(doc)
    _ch2_objectives(doc)
    page_break(doc)
    _ch3_literature(doc)
    page_break(doc)
    _ch4_existing(doc)
    page_break(doc)
    _ch5_architecture(doc)


# ── Chapter 1 ─────────────────────────────────────────────────────────────
def _ch1_introduction(doc):
    heading(doc, 'CHAPTER 1: Introduction', level=1)

    heading(doc, '1.1 Background', level=2)
    para(doc, 'Software development has evolved dramatically over the past two decades, moving from '
         'monolithic architectures to complex distributed systems comprising millions of lines of '
         'code. As software systems grow in scale and complexity, the challenge of ensuring their '
         'security and quality has become increasingly critical. According to the National '
         'Vulnerability Database, thousands of new software vulnerabilities are reported each '
         'year, many of which arise from well-understood, preventable coding mistakes such as '
         'SQL injection, path traversal, and improper input validation.')

    para(doc, 'Traditional code review—in which developers manually inspect code for defects—'
         'remains a cornerstone of software quality assurance. However, manual review is '
         'resource-intensive, inconsistent across reviewers, and poorly suited to the volume '
         'and velocity of modern development workflows. A survey of software developers reported '
         'that developers spend an average of 6.4 hours per week on code review [2], representing '
         'a substantial cost for development teams of any size.')

    heading(doc, '1.2 Static Application Security Testing', level=2)
    para(doc, 'Static Application Security Testing (SAST) tools address these challenges by '
         'analysing source code automatically, without executing it, to identify potential '
         'vulnerabilities and code quality issues. Tools such as Semgrep, SonarQube, and '
         'GitHub CodeQL have demonstrated the ability to detect common vulnerability classes '
         'at scale. However, SAST tools present a fundamental usability challenge: their output '
         'consists of rule identifiers, file paths, and line numbers, with minimal contextual '
         'explanation of why a finding matters, how exploitable it is, or how a developer should '
         'respond to it.')

    para(doc, 'Research has demonstrated that SAST tool performance varies significantly. '
         'Bennett et al. [6] found that individual SAST tools detected between 11.2% and 26.5% '
         'of known vulnerabilities in their evaluation dataset, with a combination of four tools '
         'reaching only 38.8% detection coverage. This highlights both the value and the '
         'limitations of rule-based static analysis as a standalone approach.')

    heading(doc, '1.3 Role of Artificial Intelligence in Code Review', level=2)
    para(doc, 'The emergence of large language models (LLMs) has created new possibilities for '
         'code analysis and review. Unlike rule-based static analysers, LLMs can understand the '
         'semantic context of code and generate natural-language explanations that are accessible '
         'to developers at all levels of expertise. Rasheed et al. [1] demonstrated that '
         'LLM-based agents can autonomously review code, identify bugs and code smells, and '
         'provide improvement suggestions beyond what traditional static analysis tools offer. '
         'Google\'s AutoCommenter system [3], deployed to tens of thousands of developers, '
         'demonstrated that automated AI-assisted code review can have a measurable positive '
         'impact on developer workflows at industrial scale.')

    para(doc, 'However, AI-generated explanations and suggested fixes introduce their own '
         'challenges: LLM outputs can be imprecise, incomplete, or incorrect, particularly for '
         'less common vulnerability types. Limbani et al. [4] found that while AI-assisted code '
         'review can improve precision and reduce review time, it may also introduce false '
         'positives and increase review duration if not carefully integrated. This reinforces '
         'the importance of explainable AI (XAI) principles—ensuring that AI-generated '
         'recommendations are accompanied by transparent reasoning that developers can evaluate.')

    heading(doc, '1.4 Introduction to Explicite AI', level=2)
    para(doc, 'Explicite AI is a full-stack web application developed to address the gap between '
         'automated vulnerability detection and developer-accessible, actionable remediation. '
         'The platform integrates static code analysis through Semgrep with AI-generated '
         'explanations, structured suggested fixes, and an interactive learning pathway, '
         'providing developers with a unified workflow from code submission to understanding '
         'and remediation.')

    para(doc, 'The name "Explicite" reflects the platform\'s core design principle: making '
         'security findings explicit, understandable, and actionable rather than presenting them '
         'as opaque rule violations. Every finding in the system can be accompanied by a '
         'structured AI explanation covering what the vulnerability is, why it matters, how it '
         'arises in code, and how it can be remediated. Suggested fixes are proposed by the AI '
         'system but require explicit developer approval before any code modification is '
         'considered, preserving human oversight throughout the workflow.')

    heading(doc, '1.5 Problem Statement', level=2)
    para(doc, 'Developers lack an integrated tool that combines static-analysis reporting with '
         'contextual AI-generated explanations, structured remediation guidance, and adaptive '
         'learning support. This absence creates a workflow disconnect in which developers must '
         'navigate between analysis reports, documentation references, and issue trackers to '
         'understand and address vulnerabilities—creating friction, inconsistency, and missed '
         'learning opportunities, particularly for developers with limited security expertise.')

    heading(doc, '1.6 Project Scope', level=2)
    para(doc, 'Explicite AI is scoped as a locally deployable web application for individual '
         'developers and small development teams. The platform supports static analysis of Python, '
         'Java, JavaScript, and TypeScript source code submitted as ZIP archives or via public '
         'HTTPS Git repository URLs. AI features require either a locally hosted Ollama instance '
         'or access to the Anthropic API. The platform does not support dynamic analysis, '
         'compiled binary analysis, private repository access, or production cloud deployment '
         'in its current form.')


# ── Chapter 2 ─────────────────────────────────────────────────────────────
def _ch2_objectives(doc):
    heading(doc, 'CHAPTER 2: Objectives and Project Scope', level=1)

    heading(doc, '2.1 Primary Objectives', level=2)
    primary = [
        'Automate source-code security analysis for Python, Java, JavaScript, and TypeScript through Semgrep 1.181.0.',
        'Detect and classify potential vulnerabilities with severity ratings (Critical, High, Medium, Low).',
        'Present categorised security and quality findings through a structured, navigable interface.',
        'Explain vulnerabilities through AI-generated structured responses covering what, why, how, remediation, and caveats.',
        'Prioritise findings using a risk scoring system based on severity weights.',
        'Calculate and display CVSS 3.1 base scores where vector metadata is available from Semgrep rules.',
        'Generate AI-assisted suggested code fixes with explicit developer approval required before application.',
        'Provide curated educational resources and structured learning paths linked to vulnerability categories.',
        'Recommend learning material personalised to the user\'s open findings using a deterministic matching algorithm.',
        'Provide an interactive multi-turn AI learning tutor for contextual developer education.',
        'Apply a consistent, usability-focused "Explicite Midnight" dark-first design system across all 11 screens.',
    ]
    for obj in primary:
        bullet(doc, obj)

    heading(doc, '2.2 Secondary Objectives', level=2)
    secondary = [
        'Reduce developer cognitive load by consolidating the analysis-to-remediation workflow in a single application.',
        'Provide an organised dashboard with aggregated project metrics including technical debt and duplication percentage.',
        'Maintain persistent analysis history enabling comparison of findings across multiple submissions.',
        'Support configurable AI providers (Ollama, Anthropic) through a single environment variable.',
        'Ensure a consistent user experience through design tokens, visual hierarchy, and clear feedback states.',
        'Implement role-based access control (viewer, developer, owner) for project membership.',
    ]
    for obj in secondary:
        bullet(doc, obj)

    heading(doc, '2.3 Target Users', level=2)
    para(doc, 'Explicite AI is designed for the following user groups:')
    users = [
        ('Developers', 'Individuals who submit source code for analysis, inspect findings, and request AI explanations and suggested fixes.'),
        ('Computer Science Students', 'Learners who use the AI tutor, learning resources, and structured explanations to develop secure coding knowledge.'),
        ('Project Team Members', 'Participants who review analysis results across a shared project using the project membership system.'),
    ]
    for role, desc in users:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.3)
        r1 = p.add_run(role + ': ')
        r1.font.bold = True
        r1.font.size = Pt(12)
        p.add_run(desc).font.size = Pt(12)

    heading(doc, '2.4 Functional Scope', level=2)
    para(doc, 'The following features are implemented and verified in the current release:')
    impl = [
        'User registration, authentication (JWT HS256), and session management',
        'Project creation with role-based membership management',
        'ZIP archive upload with security validation (magic bytes, decompression bomb detection, path traversal prevention)',
        'Public HTTPS Git repository clone with SSRF protection (DNS validation, private IP blocking)',
        'Asynchronous Semgrep analysis with background job execution and status polling',
        'Vulnerability findings storage with severity, issue type, file path, and line number',
        'CVSS 3.1 base score computation from Semgrep rule metadata',
        'Technical debt estimation and code duplication detection',
        'AI-generated structured vulnerability explanations with adjustable expertise level',
        'AI assistant chat for project-scoped questions',
        'AI-generated suggested code fixes with approval/rejection workflow',
        'Learning resources, learning paths, and progress tracking',
        'Personalised learning recommendations based on open findings',
        'Multi-turn AI tutor sessions with persistent conversation history',
        'User settings including appearance (light/dark mode) and AI level preference',
    ]
    for item in impl:
        bullet(doc, item)

    heading(doc, '2.5 Out-of-Scope Functionality', level=2)
    out_of_scope = [
        'Dynamic Application Security Testing (DAST)',
        'Binary or bytecode analysis',
        'Private Git repository access',
        'Real-time IDE plugin integration',
        'Production cloud deployment or multi-tenancy',
        'CI/CD pipeline integration',
        'Automated patch application (all fixes require explicit developer approval)',
        'Support for languages beyond Python, Java, JavaScript, and TypeScript',
        'Formal user satisfaction studies or A/B testing',
    ]
    for item in out_of_scope:
        bullet(doc, item)


# ── Chapter 3 ─────────────────────────────────────────────────────────────
def _ch3_literature(doc):
    heading(doc, 'CHAPTER 3: Literature Review', level=1)

    heading(doc, '3.1 Overview', level=2)
    para(doc, 'This chapter reviews eight research papers directly relevant to Explicite AI\'s '
         'core areas: AI-powered code review, LLM-based code analysis, explainability in software '
         'engineering tools, static application security testing, deep learning for vulnerability '
         'detection, and automated program repair. Four papers were supplied with the project; '
         'four additional verified papers have been identified and reviewed.')

    # --- Paper 1 ---
    heading(doc, '3.2 Paper 1: AI-Powered Code Review with LLMs: Early Results', level=2)
    para(doc, 'Rasheed, Z., Abdul Sami, M., Waseem, M., Kemell, K., Wang, X., Nguyen, A., '
         'Systä, K., and Abrahamsson, P. (2024). "AI-powered Code Review with LLMs: Early '
         'Results." arXiv preprint arXiv:2404.18496. Tampere University et al. [1]')

    para(doc, 'This paper presents a multi-agent LLM-based system for autonomous code review. '
         'The system comprises four specialised agents: a Code Review Agent, Bug Report Agent, '
         'Code Smell Agent, and Code Optimisation Agent, each leveraging GPT-4 to perform '
         'distinct analysis tasks and communicate through a centralised coordination component. '
         'Unlike traditional static analysis, the proposed system can anticipate potential future '
         'risks in code and provide dual benefits: enhanced code quality and developer learning.')

    para(doc, 'The study demonstrates that LLM-based agents can go beyond pattern matching to '
         'provide contextual feedback on best practices, coding standards, and code optimisation '
         'opportunities. A key finding is that the system supports developer learning by promoting '
         'understanding of effective coding techniques, not merely identifying issues. The authors '
         'identify the absence of LLM-specific tools for code review as a significant gap in '
         'existing research.')

    para(doc, 'Limitations include the absence of an empirical evaluation with real developers, '
         'reliance on a proprietary model (GPT-4), and the experimental nature of the early '
         'results. The relevance to Explicite AI is direct: the paper supports the core design '
         'principle that AI explanations should promote developer understanding rather than simply '
         'surfacing findings.')

    # --- Paper 2 ---
    heading(doc, '3.3 Paper 2: Automated Code Review Using LLMs with Symbolic Reasoning', level=2)
    para(doc, 'İçöz, B. and Biricik, G. (2025). "Automated Code Review Using Large Language '
         'Models with Symbolic Reasoning." IEEE, 979-8-3315-1482-2/25. Yıldız Technical '
         'University, Istanbul. [2]')

    para(doc, 'This IEEE paper proposes a hybrid approach that integrates symbolic reasoning '
         'techniques with LLMs to automate the code review process. The study evaluates '
         'CodeT5, CodeBERT, and GraphCodeBERT on the CodexGlue Python defect detection '
         'dataset under four conditions: base model, few-shot learning, fine-tuned model, '
         'and a hybrid approach combining symbolic knowledge maps with fine-tuned models.')

    para(doc, 'Results show that GraphCodeBERT with the hybrid approach achieved the highest '
         'performance with accuracy of 68.7%, precision of 0.485, and F1-score of 0.381. '
         'The hybrid approach improved accuracy by up to 27.46% compared to the base model. '
         'The paper identifies a key limitation of LLMs: their tendency to produce '
         'semantically limited results and hallucinations in code review tasks. The symbolic '
         'reasoning component, implemented as a knowledge map embedded in prompts, provides '
         'additional context that guides models toward more logical findings.')

    para(doc, 'Relevance to Explicite AI: this work informs the platform\'s approach of '
         'combining Semgrep\'s rule-based static analysis with LLM-generated explanations, '
         'creating a hybrid system that benefits from both the reliability of pattern-based '
         'tools and the contextual reasoning of language models.')

    # --- Paper 3 ---
    heading(doc, '3.4 Paper 3: AI-Assisted Assessment of Coding Practices (AutoCommenter)', level=2)
    para(doc, 'Vijayvergiya, M., Salawa, M., Budiselić, I., Zheng, D., Lamblin, P., '
         'Ivanković, M., Carin, J., Lewko, M., Andonov, J., Petrović, G., Tarlow, D., '
         'Maniatis, P., and Just, R. (2024). "AI-Assisted Assessment of Coding Practices in '
         'Modern Code Review." AIware \'24, July 15–16, 2024, Porto de Galinhas, Brazil. '
         'ACM. [3]')

    para(doc, 'This paper reports on the development, deployment, and evaluation of '
         'AutoCommenter, a large-scale LLM-based code review system deployed to tens of '
         'thousands of developers at Google. AutoCommenter automatically learns and enforces '
         'coding best practices for C++, Java, Python, and Go by detecting violations and '
         'generating automated code review comments.')

    para(doc, 'The system employs a T5-based large sequence model trained on over 3 billion '
         'examples, fine-tuned on historical code review comment data. The model detects '
         'violations by predicting the code location and the URL of the violated best practice. '
         'Evaluation showed a positive impact on developer workflow and confirmed the feasibility '
         'of end-to-end automated best-practice enforcement at industrial scale. Key lessons '
         'include the importance of calibrating confidence thresholds to maintain acceptable '
         'false positive rates and the engineering challenges of deploying such a system at scale.')

    para(doc, 'Limitations include reliance on a large proprietary infrastructure, computational '
         'cost of continuous model retraining, and the challenge of managing an ever-evolving '
         'set of best practice guidelines. Relevance: AutoCommenter\'s architecture validates '
         'Explicite AI\'s design of a backend AI service layer with a swappable provider '
         'abstraction, and its lessons on confidence thresholds inform the platform\'s '
         'handling of AI output validation.')

    # --- Paper 4 ---
    heading(doc, '3.5 Paper 4: AI-Assisted Code Reviews on Developer Productivity', level=2)
    para(doc, 'Limbani, R.Y., Adityakumar, P., and Basit, S.M. (2025). "Evaluating The Impact '
         'Of AI-Assisted Code Reviews On Developer Productivity And Code Quality." '
         'International Journal of Creative Research Thoughts (IJCRT), Volume 13, Issue 4, '
         'April 2025, ISSN: 2320-2882. Article ID: IJCRT25A4167. [4]')

    para(doc, 'This paper evaluates how AI-assisted code review platforms affect developer '
         'productivity and code quality by integrating GPT-4, CodeBERT, and CodeT5 with '
         'traditional static analysis tools (Pylint, ESLint). The study presents an AI '
         'platform evaluated on benchmark code snippets containing known issues, measuring '
         'review time, Acc@k, Precision@1, and Average Precision against baseline automated '
         'systems.')

    para(doc, 'Results show that the AI platform achieved Precision@1 of 95% versus the '
         'baseline, and reduced review time from 15 seconds to 10 seconds per snippet. '
         'However, Acc@k (86%) was slightly lower than the baseline (93%), suggesting that '
         'while the AI platform provides more precise and actionable feedback, it may '
         'occasionally miss exact fault locations. A central finding is that Explainable AI '
         '(EAI) principles—providing natural-language justifications for findings—are critical '
         'for developer trust and adoption. Without explanations, even accurate AI outputs '
         'may be ignored or mistrusted.')

    para(doc, 'Limitations include a small benchmark dataset and the fact that results may '
         'not generalise to complex real-world codebases. Relevance: this paper directly '
         'supports Explicite AI\'s structured five-field explanation format (what, why, '
         'how, remediation, caveats) as a concrete implementation of EAI principles.')

    # --- Paper 5 ---
    heading(doc, '3.6 Paper 5: VulDeePecker – Deep Learning for Vulnerability Detection', level=2)
    para(doc, 'Li, Z., Zou, D., Xu, S., Ou, X., Jin, H., Wang, S., Deng, Z., and Zhong, Y. '
         '(2018). "VulDeePecker: A Deep Learning-Based System for Vulnerability Detection." '
         'Proceedings of the 25th Annual Network and Distributed System Security Symposium '
         '(NDSS 2018), San Diego, CA, 18–21 February 2018. DOI: 10.14722/ndss.2018.23158. [5]')

    para(doc, 'VulDeePecker is a pioneering deep learning system for automated vulnerability '
         'detection in C/C++ source code. The system introduces the concept of "code gadgets"—'
         'groups of semantically related lines of code that need not be consecutive—as the '
         'fundamental input unit for a bidirectional LSTM network. The authors also contribute '
         'the first vulnerability dataset designed specifically for deep learning approaches.')

    para(doc, 'Evaluated on CWE-119 (buffer error) and CWE-399 (resource management error), '
         'VulDeePecker achieved significantly fewer false negatives than traditional tools '
         'while maintaining reasonable false positive rates. Applied to real-world software '
         '(Xen, Seamonkey, Libav), the system detected four previously unreported '
         'vulnerabilities that had been silently patched by vendors without NVD disclosure, '
         'demonstrating its practical detection capability.')

    para(doc, 'Limitations include restricted language support (C/C++ only), focus on '
         'specific CWE classes, and the requirement for labelled training data that may '
         'not cover emerging vulnerability types. Relevance to Explicite AI: VulDeePecker\'s '
         'work on code gadgets and semantic feature extraction informs the conceptual '
         'foundation of relating vulnerability detection to meaningful code units—a principle '
         'reflected in Explicite AI\'s per-finding file path and line number attribution.')

    # --- Paper 6 ---
    heading(doc, '3.7 Paper 6: Semgrep* – Improving SAST Tool Performance', level=2)
    para(doc, 'Bennett, G., Hall, T., Winter, E., and Counsell, S. (2024). "Semgrep*: '
         'Improving the Limited Performance of Static Application Security Testing (SAST) '
         'Tools." Proceedings of the 28th International Conference on Evaluation and '
         'Assessment in Software Engineering (EASE 2024 / SECUTE Workshop), Salerno, Italy. '
         'ACM, pp. 614–623. DOI: 10.1145/3661167.3661262. [6]')

    para(doc, 'This paper directly evaluates the performance limitations of SAST tools, '
         'including Semgrep, on production code with known vulnerabilities. Using a manually '
         'curated dataset, the authors found that individual SAST tools detected only 11.2%–'
         '26.5% of vulnerabilities. Combining four tools improved coverage to 38.8%. The '
         'authors then authored custom Semgrep rules targeting detected gaps, producing a '
         'tuned version ("Semgrep*") that detected 44.7% of vulnerabilities—a 181% improvement '
         'over the original Semgrep detection rate.')

    para(doc, 'The study also describes a containerised DevSecOps pipeline for injecting '
         'known vulnerabilities and benchmarking SAST tools systematically. A key finding '
         'is that the performance of rule-based tools is highly dependent on the quality '
         'and coverage of their rule sets, and that domain-specific rule authoring can '
         'substantially improve detection.')

    para(doc, 'Relevance to Explicite AI: this paper provides direct evidence supporting '
         'the platform\'s design rationale for AI-augmented analysis. When Semgrep alone '
         'detects fewer than half of known vulnerabilities, AI-generated contextual explanations '
         'and developer education become important tools for filling the gap between automated '
         'detection and comprehensive security awareness.')

    # --- Paper 7 ---
    heading(doc, '3.8 Paper 7: Automated Repair of Programs from LLMs', level=2)
    para(doc, 'Fan, Z., Gao, X., Mirchev, M., Roychoudhury, A., and Tan, S.H. (2023). '
         '"Automated Repair of Programs from Large Language Models." Proceedings of the '
         '45th IEEE/ACM International Conference on Software Engineering (ICSE 2023), '
         'Melbourne, Australia. IEEE/ACM, pp. 1469–1481. DOI: 10.1109/ICSE48619.2023.00128. [7]')

    para(doc, 'This ICSE 2023 paper systematically studies whether automated program repair '
         '(APR) techniques can fix incorrect solutions generated by language models in '
         'competitive programming contexts (LeetCode). The authors evaluate whether Codex '
         '(edit mode) and conventional Java APR tools (TBar, Recoder) can automatically '
         'repair LLM-produced code with fault location information.')

    para(doc, 'Results show that Codex\'s edit mode performs comparably to or better than '
         'the Java repair tools when given fault location information. The paper demonstrates '
         'that automated repair of LLM-generated code is feasible but that the quality of '
         'the repair depends heavily on the accuracy of fault localisation. This finding '
         'is directly applicable to the challenge of validating AI-generated suggested fixes.')

    para(doc, 'Limitations include the constrained evaluation context (competitive programming '
         'problems with automated test cases) which may not generalise to complex, real-world '
         'security vulnerabilities. Relevance to Explicite AI: this paper supports the '
         'platform\'s fix workflow design, where proposed fixes require developer review and '
         'approval rather than automated application—acknowledging that LLM-generated fixes '
         'have meaningful error rates.')

    # --- Paper 8 ---
    heading(doc, '3.9 Paper 8: Towards Explainable Vulnerability Detection with LLMs', level=2)
    para(doc, 'Mao, Q., Li, Z., Hu, X., Liu, K., Xia, X., and Sun, J. (2024). "Towards '
         'Explainable Vulnerability Detection with Large Language Models." arXiv preprint '
         'arXiv:2406.09701, Zhejiang University / York University. Submitted June 2024. [8]')

    para(doc, 'This paper proposes LLMVulExp, a teacher-student framework in which a '
         '"teacher" LLM generates structured explanation data for vulnerability findings, '
         'which is then used to train a "student" model capable of both detecting and '
         'explaining vulnerabilities. The framework introduces an evaluation protocol for '
         'AI-generated explanations using three metrics: Accuracy, Clarity, and Actionability, '
         'assessed through an LLM-as-judge approach.')

    para(doc, 'Evaluated on the SeVC dataset, LLMVulExp achieved over 90% F1 score on '
         'vulnerability detection while generating explanations rated significantly higher '
         'on all three quality metrics than baseline approaches. The paper demonstrates '
         'that structured explanations—not merely vulnerability labels—are achievable '
         'through LLM-based approaches and that the quality of explanations can be '
         'systematically measured.')

    para(doc, 'Limitations include the preprint status (no peer-reviewed venue confirmed '
         'at time of writing), dataset scope, and the resource requirements for the '
         'teacher-student training process. Relevance to Explicite AI: LLMVulExp\'s '
         'five-dimension explanation framework (analogous to Explicite AI\'s what/why/how/'
         'remediation/caveats structure) and its emphasis on actionable explanations '
         'directly validates the platform\'s structured explanation design.')

    # Comparison table
    heading(doc, '3.10 Literature Comparison', level=2)
    para(doc, 'The following table summarises the eight reviewed papers across key dimensions '
         'relevant to Explicite AI:')

    add_table(doc,
        headers=['#', 'Authors (Year)', 'Research Area', 'Key Contribution', 'Limitations', 'Relevance'],
        rows=[
            ['[1]', 'Rasheed et al. (2024)', 'LLM Code Review', 'Multi-agent GPT-4 review', 'No empirical eval', 'AI explanation design'],
            ['[2]', 'İçöz & Biricik (2025)', 'Hybrid Code Review', 'Symbolic+LLM hybrid', 'Limited dataset', 'Hybrid analysis rationale'],
            ['[3]', 'Vijayvergiya et al. (2024)', 'Industrial AI Review', 'AutoCommenter at Google scale', 'Proprietary infrastructure', 'Provider abstraction design'],
            ['[4]', 'Limbani et al. (2025)', 'AI Review Impact', 'EAI for developer trust', 'Small benchmark', 'Structured explanations'],
            ['[5]', 'Li et al. (2018)', 'Vuln Detection ML', 'Code gadgets + LSTM', 'C/C++ only', 'Per-finding attribution'],
            ['[6]', 'Bennett et al. (2024)', 'SAST Evaluation', 'Semgrep* rule authoring', 'Curated dataset', 'AI augmentation rationale'],
            ['[7]', 'Fan et al. (2023)', 'Program Repair', 'APR for LLM code', 'Constrained eval', 'Fix approval workflow'],
            ['[8]', 'Mao et al. (2024)', 'XAI + Vuln Detection', 'Teacher-student XAI', 'Preprint only', 'Explanation structure'],
        ],
        col_widths=[0.35, 1.7, 1.4, 1.8, 1.5, 1.5])

    heading(doc, '3.11 Research Gap Analysis', level=2)
    para(doc, 'The reviewed literature reveals several consistent gaps that Explicite AI '
         'is designed to address:')
    gaps = [
        ('Absence of integrated explanation-analysis tools', 'Existing SAST tools detect vulnerabilities but do not explain them in developer-accessible terms. LLM explanation systems exist but are not integrated with static analysis pipelines.'),
        ('Separation between detection and remediation', 'Static analysers report findings; developers must separately seek remediation guidance. No single tool closes this loop from detection to explanation to fix to learning.'),
        ('Limited support for developer education', 'Commercial SAST tools are not designed as educational platforms. VulDeePecker and LLMVulExp focus on detection accuracy rather than developer learning outcomes.'),
        ('Difficulty prioritising findings', 'Without risk scores, severity ratings, and CVSS scores presented together, developers cannot effectively prioritise which findings to address first.'),
        ('Accessibility for less experienced developers', 'SAST outputs are designed for security experts. Adjustable explanation levels and interactive tutor sessions, as implemented in Explicite AI, are not features of existing tools.'),
    ]
    for gap_title, gap_desc in gaps:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.3)
        r1 = p.add_run(gap_title + ': ')
        r1.font.bold = True
        r1.font.size = Pt(12)
        p.add_run(gap_desc).font.size = Pt(12)


# ── Chapter 4 ─────────────────────────────────────────────────────────────
def _ch4_existing(doc):
    heading(doc, 'CHAPTER 4: Existing Systems and Competitor Analysis', level=1)

    heading(doc, '4.1 Overview of Existing Approaches', level=2)
    para(doc, 'The automated code security analysis market encompasses a range of tools from '
         'open-source rule engines to enterprise SAST platforms. Each tool represents a '
         'different trade-off between analysis depth, language support, deployment model, '
         'and developer-facing features. This chapter reviews five established tools and '
         'positions Explicite AI relative to them.')

    # SonarQube
    heading(doc, '4.2 SonarQube', level=2)
    para(doc, 'SonarQube is a widely deployed open-source (Community Edition) and commercial '
         'static analysis platform supporting over 30 programming languages. It performs '
         'continuous code quality and security analysis, detecting bugs, code smells, and '
         'security hotspots. SonarQube integrates with CI/CD pipelines and provides a web '
         'dashboard with quality gates, historical trend analysis, and issue management. '
         'The commercial editions include AI-generated suggestions and extended security '
         'rule sets. SonarQube does not natively provide structured natural-language '
         'explanations of individual findings or developer learning pathways.')

    # Snyk Code
    heading(doc, '4.3 Snyk Code', level=2)
    para(doc, 'Snyk Code is a commercial SAST tool that combines semantic code analysis with '
         'AI-powered fix suggestions. It supports real-time IDE integration (VS Code, '
         'IntelliJ), pull request analysis, and CI/CD pipeline integration. Snyk Code '
         'provides fix recommendations and natural-language descriptions for findings, '
         'making it one of the closer commercial analogues to Explicite AI\'s explanation '
         'approach. However, it does not provide structured multi-field explanations '
         'covering why a vulnerability matters and how it arises, nor does it provide an '
         'educational tutor or learning pathway integrated into the analysis workflow.')

    # Semgrep
    heading(doc, '4.4 Semgrep', level=2)
    para(doc, 'Semgrep is an open-source, pattern-based static analysis engine that forms '
         'the analysis backbone of Explicite AI. As a standalone tool, Semgrep executes '
         'rule sets against source code and produces findings with severity, rule ID, file '
         'path, and line number. Semgrep OSS does not provide AI-generated explanations, '
         'risk prioritisation beyond rule severity, or suggested fixes. Semgrep Code '
         '(commercial) adds some AI-powered features. The open-source version, as used in '
         'Explicite AI, is entirely dependent on rule quality and provides no contextual '
         'developer guidance beyond the rule description string.')

    # CodeQL
    heading(doc, '4.5 GitHub CodeQL', level=2)
    para(doc, 'CodeQL is GitHub\'s semantic code analysis engine that models source code '
         'as a queryable database, enabling complex data-flow and control-flow queries. '
         'CodeQL is highly effective for detecting complex vulnerability classes that '
         'require cross-function data flow analysis. It is integrated into GitHub Advanced '
         'Security and supports C, C++, C#, Java, JavaScript, Python, Ruby, and Swift. '
         'CodeQL does not provide developer-facing AI explanations of individual findings, '
         'suggested fixes, or learning resources in its standard integration.')

    # Checkmarx
    heading(doc, '4.6 Checkmarx', level=2)
    para(doc, 'Checkmarx is a commercial enterprise SAST platform offering broad language '
         'support, CI/CD integration, and compliance reporting. The Checkmarx One platform '
         'includes AI-powered features such as AI-generated remediation guidance and '
         'correlation with open-source dependency risks. It is designed for enterprise '
         'security teams rather than individual developers or students, and its pricing '
         'model reflects this positioning. Checkmarx provides remediation guidance but '
         'does not offer an integrated learning pathway or interactive tutor.')

    # Comparison table
    heading(doc, '4.7 Competitor Comparison Matrix', level=2)
    para(doc, 'Table 3 compares the six tools across key dimensions. Feature availability '
         'is assessed based on official documentation and publicly available information '
         'as of 2025–2026. "Partial" indicates limited or commercial-tier-only availability.')

    add_table(doc,
        headers=['Feature', 'SonarQube', 'Snyk Code', 'Semgrep', 'CodeQL', 'Checkmarx', 'Explicite AI'],
        rows=[
            ['Static Analysis',          '✓', '✓', '✓', '✓', '✓', '✓'],
            ['Multi-language Support',   '✓', '✓', '✓', '✓', '✓', 'Partial (4)'],
            ['AI Explanations',          '~', '~', '✗', '✗', '~', '✓'],
            ['Structured Explanation',   '✗', '✗', '✗', '✗', '✗', '✓'],
            ['Risk / CVSS Scoring',      '✓', '✓', '~', '~', '✓', '✓'],
            ['Suggested Fixes',          '~', '✓', '✗', '✗', '~', '✓ (advisory)'],
            ['Developer Learning',       '✗', '✗', '✗', '✗', '✗', '✓'],
            ['Interactive AI Tutor',     '✗', '✗', '✗', '✗', '✗', '✓'],
            ['CI/CD Integration',        '✓', '✓', '✓', '✓', '✓', '✗ (planned)'],
            ['Open Source / Free Tier',  '✓', '~', '✓', '✓', '✗', '✓'],
            ['Git Repo Analysis',        '~', '✓', '~', '✓', '✓', '✓'],
        ],
        col_widths=[1.8, 0.95, 0.95, 0.85, 0.85, 1.0, 1.1])
    para(doc, 'Note: ✓ = Supported; ~ = Partial/Commercial Tier; ✗ = Not Available. '
         'Competitor feature assessment based on official documentation (2025–2026). '
         'Explicite AI\'s suggested fixes are advisory only and require explicit developer approval.',
         align=WD_ALIGN_PARAGRAPH.LEFT)

    heading(doc, '4.8 Positioning and Differentiation', level=2)
    para(doc, 'Explicite AI occupies a distinct position in this landscape: it is the only '
         'tool in the comparison that integrates structured AI explanations, advisory '
         'suggested fixes, and an interactive developer learning pathway in a single open '
         'application. Its differentiation is not in analysis depth—commercial tools such '
         'as Checkmarx and CodeQL offer more comprehensive analysis capabilities—but in '
         'its focus on making vulnerability findings understandable, actionable, and '
         'educational for developers at all experience levels.')

    para(doc, 'Importantly, Explicite AI does not claim to outperform commercial SAST '
         'platforms in detection accuracy. Its intended use case is as an educational and '
         'developer-assistance platform that augments rather than replaces specialised '
         'security tooling. The advisory nature of its AI-generated fixes, combined with '
         'mandatory developer approval, reflects a design philosophy of human oversight '
         'preservation rather than fully automated remediation.')


# ── Chapter 5 ─────────────────────────────────────────────────────────────
def _ch5_architecture(doc):
    heading(doc, 'CHAPTER 5: Proposed System and System Architecture', level=1)

    heading(doc, '5.1 System Overview', level=2)
    para(doc, 'Explicite AI is implemented as a three-tier web application comprising a '
         'React frontend, a FastAPI backend, and a PostgreSQL database, with external '
         'integrations to the Semgrep analysis engine and a configurable AI provider layer. '
         'All communication between tiers occurs via HTTPS/JSON REST API calls. The system '
         'is designed for local deployment with clear separation of concerns between the '
         'user interface, business logic, data persistence, and external analysis services.')

    heading(doc, '5.2 System Architecture', level=2)
    para(doc, 'The three-tier architecture is structured as follows:')
    para(doc, 'Browser / Frontend (port 8443): The React 19 and TypeScript frontend '
         'communicates with the backend exclusively through the api.ts HTTP client module. '
         'Navigation between 11 screens is managed by a custom NavCtx React context, '
         'eliminating the need for a routing library. JWT tokens are stored in '
         'sessionStorage under the key "explicite_token". The Explicite Midnight design '
         'system is implemented through Tailwind CSS v4 with --xm-* CSS custom properties '
         'supporting light and dark theme modes via a data-theme HTML attribute.')

    para(doc, 'Backend / API Layer (port 8000): The FastAPI application provides RESTful '
         'endpoints under the /api/v1 prefix. Authentication uses JWT HS256 bearer tokens '
         'with configurable expiry. Role-based access control is enforced at the '
         'dependency injection layer (deps.py), where the get_project_membership() function '
         'validates the current user\'s membership and role before any project-scoped '
         'operation proceeds. Analysis jobs execute asynchronously as background tasks, '
         'returning HTTP 202 immediately and storing results in the database upon completion.')

    para(doc, 'Persistence Layer (port 5434): PostgreSQL 16 running in a Docker container '
         'stores all application data. SQLAlchemy 2.x async ORM with the asyncpg driver '
         'handles all database interactions. Alembic manages the schema migration chain '
         'with nine migrations from the initial schema to the current head (c1d2e3f4a5b6).')

    para(doc, 'External Services: Semgrep 1.181.0 executes as a subprocess within the '
         'backend\'s virtual environment. AI services (Ollama at localhost:11434 or the '
         'Anthropic API) are accessed through a provider abstraction layer in ai_service.py, '
         'switchable via the LLM_PROVIDER environment variable.')

    heading(doc, '5.3 Data Flow', level=2)
    para(doc, 'The primary analysis workflow follows an asynchronous pipeline:')
    steps = [
        'Developer authenticates via POST /api/v1/auth/login; receives a JWT bearer token.',
        'Developer selects or creates a project; project membership is verified server-side.',
        'Developer submits code via POST /api/v1/projects/{id}/analyse (ZIP) or /analyse/git (Git URL).',
        'Backend creates an AnalysisJob record with status "queued" and returns HTTP 202.',
        'Background task executes: source is extracted/cloned, Semgrep analyses the source tree.',
        'Findings, metrics (technical debt, duplication), and CVSS scores are stored in the database.',
        'Frontend polls GET /api/v1/projects/{id}/analyse/{job_id} until status is "completed" or "failed".',
        'Developer inspects findings, requests AI explanations, generates suggested fixes, and accesses learning resources.',
    ]
    for i, step in enumerate(steps, 1):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.3)
        r = p.add_run(f'{i}. ')
        r.font.bold = True
        r.font.size = Pt(12)
        p.add_run(step).font.size = Pt(12)
        p.paragraph_format.space_after = Pt(4)

    figure(doc, ASSETS / 'fig06_analysis_workflow.png',
           'Figure 6: Explicite AI Code Analysis Workflow (Source: Project implementation)', 6.0)

    heading(doc, '5.4 Security Architecture', level=2)
    para(doc, 'Security controls are implemented at multiple layers:')
    sec_controls = [
        ('Input validation', 'Pydantic v2 schemas validate all request bodies; ZIP archives are checked for magic bytes, decompression bomb ratios (>100:1), and entry count limits (max 1,000).'),
        ('SSRF protection', 'Git repository URLs must use HTTPS. The git_service.py module performs DNS resolution and validates all resolved IP addresses against private ranges (RFC 1918, loopback, link-local) before initiating a clone operation.'),
        ('Safe process execution', 'Semgrep is invoked with a fixed argument list using shell=False, preventing injection via user-controlled file paths.'),
        ('Source isolation', 'Extracted source is processed in temporary directories. source_path is never included in any API response. The .git/ directory is removed after clone.'),
        ('Fix safety', 'No fix is applied without explicit developer approval. Stale-source detection compares a SHA-256 hash of the original file at approval time against the hash recorded at fix generation time.'),
        ('AI output handling', 'Finding data is labelled as DATA in LLM prompts as an injection mitigation. Model output is validated for required fields and length limits before storage.'),
    ]
    for control, desc in sec_controls:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.3)
        r1 = p.add_run(control + ': ')
        r1.font.bold = True
        r1.font.size = Pt(12)
        p.add_run(desc).font.size = Pt(12)
        p.paragraph_format.space_after = Pt(4)

    heading(doc, '5.5 Database Entity Relationship', level=2)
    para(doc, 'The database schema comprises eight primary entities with the following '
         'relationships:')
    entities = [
        ('users', 'Stores user credentials (hashed), preferences, and system role. One-to-many with project memberships.'),
        ('projects', 'Stores project metadata. Associated with users through the project_memberships join entity.'),
        ('project_memberships', 'Join entity linking users to projects with role assignment (viewer/developer/owner).'),
        ('analysis_jobs', 'Stores analysis job state, status, source metadata, repo_url (nullable), metrics, and timestamps. One-to-many with findings.'),
        ('findings', 'Stores individual vulnerability findings with severity, issue type, file path, line numbers, rule key, CVSS vector, and status.'),
        ('suggested_fixes', 'Stores AI-generated fix proposals including proposed_lines, rationale, caveats, original_hash, and approval status.'),
        ('learning_resources / learning_paths', 'Stores educational content and structured learning sequences. Many-to-many through learning_path_resources.'),
        ('tutor_sessions / tutor_messages', 'Stores multi-turn AI tutor conversations with resource context and message history.'),
    ]
    add_table(doc,
        headers=['Entity', 'Description'],
        rows=entities,
        col_widths=[1.9, 4.7])

    heading(doc, '5.6 AI Explanation Architecture', level=2)
    para(doc, 'The AI service layer (ai_service.py) implements a provider abstraction '
         'pattern. The AIProvider abstract base class defines the interface: '
         'generate_explanation(), generate_fix(), and chat(). Concrete implementations '
         'are OllamaProvider and AnthropicProvider, both implementing identical method '
         'signatures. A NoneProvider returns honest 503 errors when no AI is configured. '
         'The active provider is selected at application startup based on LLM_PROVIDER '
         'and requires no API or frontend changes to switch between providers.')

    para(doc, 'System prompts explicitly label finding data as DATA rather than instructions, '
         'as a prompt injection mitigation measure. Explanation responses are validated for '
         'all five required JSON fields (what, why, how_it_arises, remediation, caveats) '
         'and each field is truncated at a maximum length before storage. Fix generation '
         'uses LLM_FIX_MAX_TOKENS=2048 (configurable) to accommodate the larger token '
         'output required for proposed code replacements.')


if __name__ == '__main__':
    doc = new_document()
    build_chapters_01_05(doc)
    out = Path(__file__).parent.parent / 'test_ch1_5.docx'
    doc.save(str(out))
    print(f'Chapters 1–5 saved: {out}')
