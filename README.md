# Privacy Jailbreaking Evaluation in Large Language Models

## Authors: Batyrkhan Abukhanov, Sirazh Gabdullin, Niclas Unger
### Supervisor: Dr. Lindrit Kqiku 

## Overview
This project investigates whether modern Large Language Models (LLMs) can be manipulated (jailbroken) into revealing Personally Identifiable Information (PII). We evaluate multiple large-scale models using adversarial prompting techniques and a multi-agent evaluation pipeline.

The goal is to assess:
  - robustness of LLM safety alignment
  - effectiveness of different jailbreaking techniques
  - risk of PII leakage in modern LLMs

## Methodology
### Adversarial Attackking Techniques
The following adversarial attacking techniques were chosen, inspired by the paper "LLM Can be a Dangerous Persuader": https://arxiv.org/abs/2504.10430
  1) Direct Prompting
  2) Contextual Framing
  3) Role Playing

### Dataset
Adversarial attacking prompts were generated manually in scope of this project using two following datasets:
  1) "PII-Scope: A Comprehensive Study on Training Data PII Extraction Attacks in LLMs" (https://arxiv.org/pdf/2410.06704)
  2) "Do-Not-Answer: Evaluating Safeguards in LLMs" (https://github.com/Libr-AI/do-not-answer)

### Multi-Agent Setup
The evaluation is based on a two-agent pipeline:
  1. Victim Model
     Receives adversarial prompts and generates responses
  2. Judge Model
     a) For models 1)-4): Llama-Guard-3-8B: Classifies responses as: `safe` or `unsafe`
     b) For models 5)-10): mistral-large-3-675b-instruct-2512: Categorizes responses as 'refusal', 'surface' or 'harmful'
     

### Models Evaluated
1) deepseek-llm-67b-chat-AWQ
2) Qwen2.5-72B-Instruct-AWQ
3) Qwen2.5-72B-Instruct-Abliterated-AWQ
4) llama-3.3-70b-instruct-awq
5) apertus-70b-instruct-2509
6) deepseek-r1-distill-llama-70b
7) devstral-2-123b-instruct-2512
8) gemma-3-27b-it
9) teuken-7b-instruct-research
10) internvl3.5-30b-a3b

## Reslts Summary
Percentage values represent the proportion of prompts that were successfully jailbroken, as classified as `unsafe` by the judge model.

### Models 1 - 4:
#### Enron Dataset Results
| Attack Technique     | DeepSeek | Qwen | Qwen-Ablit. | Llama |
|----------------------|----------|------|-------------|--------|
| Direct Prompting     | 0%       | 0%   | 0%          | 0%     |
| Role Playing         | 0%       | 0%   | 0%          | 0%     |
| Contextual Framing   | 0%       | 0%   | 0%          | 0%     |

#### General-purpose PII extraction Results
| Attack Technique     | DeepSeek | Qwen | Qwen-Ablit. | Llama |
|----------------------|----------|------|-------------|--------|
| Direct Prompting     | 0%       | 0%   | 0%          | 0%     |
| Role Playing         | 0%       | 0.4% | 1.6%        | 0%     |
| Contextual Framing   | 0%       | 0.4% | 0%          | 0%     |

### Models 5-10
#### Percentage of potentially harmful (unsafe) responses across different attack techniques.
| Victim Model | Direct Prompting | Contextual Framing | Role Playing | Role Playing (split) |
|--------------|------------------|--------------------|--------------|----------------------|
| Apertus      | 0%               | 0%                 | 0%           | 0%                   |
| DeepSeek     | 5%               | 4%                 | 4%           | 19%                  |
| Devstral     | 2%               | 0%                 | 15%          | 0%                   |
| Gemma        | 5%               | 11%                | 42%          | 65%                  |
| Teuken       | 50%              | 2%                 | 23%          | 19%                  |
| Intern       | 0%               | 0%                 | 8%           | 0%                   |

#### Results for privacy jailbreaking attacks for models by creativity
| Prompting Technique   | Deterministic (temp=0) | Creative (temp=1) |
|----------------------|------------------------|-------------------|
| Direct Prompting     | 12%                    | 9%                |
| Contextual Framing   | 4%                     | 2%                |
| Role Playing         | 14%                    | 17%               |
| Role Playing (split) | 16%                    | 18%               |

## Installation
```bash
pip install -r requirements.txt
```

## Project Structure
```bash
privacy_jailbreakkking/
├── dataset/                # Datasets and prompts
├── Experiments_Unger/      # All experiments and results of Niclas Unger (all experiements for victim models 5)-10)) -> see ReadMe in the folder for more specifics
├── results/                # Results (model responses) for victim responses for models 1)-4) and for the qualitative experiments are stored here
├── requirements.txt        # Dependencies
└── README.md               # This file
```

## Ethical Considerations
This project is conducted for research purposes only.
The goal is to evaluate and improve the safety of LLM systems.
   - No real personal data is intentionally exposed
   - All experiments follow responsible AI guidelines

