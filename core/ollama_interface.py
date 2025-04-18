import subprocess

def ask_llm(prompt):
    result = subprocess.run(
        ["ollama", "run", "mistral", "--", prompt],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
