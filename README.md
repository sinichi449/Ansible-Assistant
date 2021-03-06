# Ansible-Assistant
Google Assistant implementation on ansible (coming soon).

# Installations
0. Clone this repo.

```bash
    $ git clone https://github.com/sinichi449/Ansible-Assistant.git
    $ cd Ansible-Assistant
```

1. [Configure a Developer Project and Account Settings](https://developers.google.com/assistant/sdk/guides/service/python/embed/config-dev-project-and-account)

2. [Register the Device Model](https://developers.google.com/assistant/sdk/guides/service/python/embed/register-device)

3. On **Device Registration**, don't forget to click `Download OAuth 2.0 credentials` which is required to generate credentials later.

4. Configure Python Virtual Environment.

```bash
    $ sudo apt-get update
    $ sudo apt-get install python3-dev python3-venv
    $ python3 -m venv env
    $ env/bin/python -m pip install --upgrade pip setuptools wheel
    $ source env/bin/activate
```

5. Install Dependencies.

```bash
    (env) $ sudo apt-get install portaudio19-dev libffi-dev libssl-dev
    (env) $ python -m pip install --upgrade google-assistant-sdk[samples]
```

6. Go to [Google Cloud Credentials](https://console.cloud.google.com/apis/credentials/). Setup the **OAuth Consent Screen** and fill all the required forms. 

7. On the **Test Users** section, click `ADD USER` and add your email.

8. Generate credentials.

```bash
    (env) $ python -m pip install --upgrade google-auth-oauthlib[tool]
    
    # change /path/to/client_secret_client-id.json to the directory of downloaded client secrets.
    (env) $ google-oauthlib-tool --scope https://www.googleapis.com/auth/assistant-sdk-prototype \
      --save --headless --client-secrets /path/to/client_secret_client-id.json
```

9. Follow the instructions URL. 

10. If you encountered **403 ERROR UNAUTHORIZED**, go back and double check steps **#6** and **#7**.

11. Back to your cloned repo directory, make the `gactions` file executable.
 
 ```bash
    (env) $ sudo chmod +x gactions
```

12. Execute below commands. Replace `project_id` with your [Project ID](https://support.google.com/cloud/answer/6158840).

```bash
    (env) $ ./gactions update --action_package actions.json --project project_id
```

13. Follow the instructions URL to authorize apps to Google Accounts.

14. Get `device_id`:

```bash
    # Replace my-dev-project and my-model
    (env) $ googlesamples-assistant-pushtotalk --project-id my-dev-project --device-model-id my-model
```
15. Pay attention to something like `INFO:root:Device registered: 928dbb4a-59b0-11ec-a926-37546axxxxx`.

16. Copy `928dbb4a-59b0-11ec-a926-37546axxxxx`.

17. Press `CTRL + C` to exit the `googlesamples-assistant-pushtotalk` program.

18. Paste `928dbb4a-59b0-11ec-a926-37546axxxxx` to `commands.py` -> `device_id`.

```bash
    (env) $ nano commands.py
```
```python
    ...
    from utils import device_helpers

    device_id = '928dbb4a-59b0-11ec-a926-37546axxxxx' # Replace this
    device_handler = device_helpers.DeviceRequestHandler(device_id)
    ...
```

19. Run the `main.py`

    ```bash
        (env) $ python3 main.py
    ```
    
20. Press `ENTER` to capture your voice command. Say something like `Create 10 folders.`

21. If nothing happens, check the step **#12** or visit `https://console.actions.google.com/project/<your-project-id>/actions/`. Make sure you've clicked **SAVE** button of all actions.
