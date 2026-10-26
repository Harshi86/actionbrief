# ActionBrief

ActionBrief turns rough meeting notes into a concise summary, decisions, action items with owners and due dates, and open questions. It is a solo-built prototype for the Nebius × NVIDIA Global AI Hackathon, Best Apps and Agents track.

## Stack and model

- Streamlit interface
- Nebius Token Factory OpenAI-compatible chat completions API
- NVIDIA Nemotron model (default: `nvidia/Nemotron-3.5-Super-VL`; use a model ID enabled for your Token Factory account)

The app sends the pasted notes to the selected model and requests a structured JSON brief. Notes are held in Streamlit session state for the current session and are not stored in a database. Do not paste sensitive information into this demo.

## How Nebius Token Factory helped

Token Factory let me use hosted NVIDIA Nemotron inference through an OpenAI-compatible API, so I could focus on the app flow and structured meeting brief instead of provisioning GPUs or serving a model myself. I used the same endpoint while iterating on the prompt and validating the notes-to-brief workflow.

## Run locally

1. Install Python 3.10 or newer.
2. Create and activate a virtual environment.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set your Nebius Token Factory API key. PowerShell:

   ```powershell
   $env:NEBIUS_API_KEY="your-token-factory-api-key"
   ```

   macOS/Linux:

   ```bash
   export NEBIUS_API_KEY="your-token-factory-api-key"
   ```

5. Start the app:

   ```bash
   streamlit run app.py
   ```

For local testing, you can paste the key into the sidebar for the current session. If you set `NEBIUS_API_KEY` in your shell instead, the app reads it as a server-side value and does not show it in the sidebar. Set `NEBIUS_MODEL` to select a different model. Never commit API keys.

## Deploy

Deploy this repository to Streamlit Community Cloud or another Streamlit host. In the app's **Settings → Secrets**, add:

```toml
NEBIUS_API_KEY = "your-token-factory-api-key"
NEBIUS_MODEL = "nvidia/Nemotron-3.5-Super-VL"
```

Use a model ID enabled for your Token Factory account. The app reads both values on the server; when a server key is configured, neither the key nor a key input field is sent to the app UI. Do not put secrets in GitHub, screenshots, or frontend code. A public app can use your project's Token Factory credits, so monitor usage and rotate or remove the key after the demo.

## Hackathon submission notes

- Track: Best Apps and Agents
- Nebius: Each brief uses a runtime inference call to Nebius Token Factory.
- NVIDIA: Configure an NVIDIA Nemotron model in the model field.
- Demo: Paste notes and generate a brief; download it as Markdown.

## License

MIT. See [LICENSE](LICENSE).
