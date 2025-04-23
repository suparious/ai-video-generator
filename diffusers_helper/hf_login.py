import os


def login(token):
    from huggingface_hub import login
    import time
    import os
    
    # Explicitly ensure HF_HUB_OFFLINE is not set
    if 'HF_HUB_OFFLINE' in os.environ:
        print(f"Current HF_HUB_OFFLINE value: {os.environ.get('HF_HUB_OFFLINE')}")
        os.environ['HF_HUB_OFFLINE'] = '0'
        print(f"Set HF_HUB_OFFLINE to: {os.environ.get('HF_HUB_OFFLINE')}")
    
    max_attempts = 5
    attempt = 0
    
    while attempt < max_attempts:
        try:
            login(token)
            print('HF login ok.')
            return
        except Exception as e:
            attempt += 1
            print(f'HF login failed: {e}. Attempt {attempt}/{max_attempts}')
            
            # Handle offline mode error specifically
            if 'offline mode is enabled' in str(e):
                print('Detected offline mode error, disabling offline mode')
                os.environ['HF_HUB_OFFLINE'] = '0'
                
                # Also try setting other offline-related variables
                os.environ['TRANSFORMERS_OFFLINE'] = '0'
                os.environ['DIFFUSERS_OFFLINE'] = '0'
                
                print(f"Updated environment: HF_HUB_OFFLINE={os.environ.get('HF_HUB_OFFLINE')}")
            
            time.sleep(1)
    
    print("Failed to login after multiple attempts. Continuing without login.")
    # Continue without login rather than getting stuck in an infinite loop


hf_token = os.environ.get('HF_TOKEN', None)

if hf_token is not None:
    login(hf_token)
