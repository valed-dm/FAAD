import queue
import random
import time

from curl_cffi.requests import errors

from core.config import settings
from core.logging_config import log

from .curl_wrapper import create_session
from .session_handler import login_to_freenet


def process_account(
    account: list, alias_pool: queue.Queue, proxy_config: dict, output_lock
):
    email, password = account
    session = create_session(proxy_config)

    added_aliases = []
    critical_error_occurred = False

    try:
        access_token = login_to_freenet(session, email, password)

        delay = random.uniform(60, 95)
        log.info(f"[{email}] Waiting for {delay:.2f} seconds...")
        time.sleep(delay)

        log.info(f"[{email}] Fetching mail accounts data...")
        auth_headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Client": "fn-cloud-web-web",
            "Origin": "https://webmail.freenet.de",
            "Referer": "https://webmail.freenet.de/",
        }

        response = session.get(
            settings.MAIL_ACCOUNTS_URL, headers=auth_headers, timeout=60
        )
        response.raise_for_status()
        accounts_data = response.json()

        if not isinstance(accounts_data.get("data"), list) or not accounts_data["data"]:
            log.warning(f"[{email}] API response invalid. Response: {accounts_data}")
            raise ValueError("Could not find 'data' array in API response.")

        primary_account_data = accounts_data["data"][0]
        correct_account_id = primary_account_data.get("account_id")

        if not correct_account_id:
            log.warning(
                f"[{email}] Could not extract account_id. Data: {primary_account_data}"
            )
            raise ValueError("Could not find correct 'account_id'")

        existing_aliases = {
            alias["email"] for alias in primary_account_data.get("aliases", [])
        }
        max_alias_limit = primary_account_data.get(
            "max_alias", settings.MAX_ALIASES_PER_ACCOUNT
        )

        log.info(
            f"[{email}] AccountID: {correct_account_id}."
            f" Found {len(existing_aliases)} aliases."
            f" Limit is {max_alias_limit}."
        )

        aliases_to_add_count = max_alias_limit - len(existing_aliases)
        if aliases_to_add_count <= 0:
            log.info(f"[{email}] Account has max aliases. No action needed.")

        while len(added_aliases) < aliases_to_add_count:
            new_alias = None
            try:
                new_alias = alias_pool.get_nowait()
            except queue.Empty:
                log.warning(f"[{email}] Alias queue empty.")
                break

            full_email = f"{new_alias}@freenet.de"
            if full_email in existing_aliases:
                log.info(f"[{email}] Alias {full_email} already on account.")
                continue

            add_payload = {
                "account_id": correct_account_id,
                "email": full_email,
                "setting": "mail.accounts.internal.alias",
            }
            log.info(
                f"[{email}] Adding alias:"
                f" {full_email} ({len(added_aliases) + 1}/{aliases_to_add_count})"
            )

            try:
                response = session.post(
                    settings.SETTINGS_URL,
                    headers=auth_headers,
                    json=add_payload,
                    timeout=45,
                )
                if response.status_code == 200:
                    log.success(f"[{email}] Added alias: {new_alias}")
                    added_aliases.append(new_alias)
                    existing_aliases.add(full_email)
                else:
                    err_data = response.json()
                    err_msg = err_data.get("message", "No error message")
                    log.warning(f"[{email}] API error adding '{new_alias}': {err_msg}.")
                    if "Ratelimit" in err_msg or err_data.get("code") == 4101:
                        log.error(
                            f"[{email}] Hit rate limit. Re-queuing '{new_alias}'."
                        )
                        alias_pool.put(new_alias)
                        break

                time.sleep(random.uniform(6, 12))

            except (errors.RequestsError, errors.CurlError) as e:
                log.error(
                    f"[{email}] Network error adding '{new_alias}': {e}."
                    f" Re-queuing alias."
                )
                if new_alias:
                    alias_pool.put(new_alias)
                break

    except Exception as e:
        critical_error_occurred = True
        error_response_text = (
            getattr(e, "response", {}).text if hasattr(e, "response") else ""
        )
        log.critical(f"[{email}] Critical error: {e}")
        with output_lock:
            with settings.CRITICAL_ERRORS_FILE.open("a", encoding="utf-8") as f:
                f.write(
                    f"{email}:{password} | Error: {e} | Response:"
                    f" {error_response_text}\n"
                )

    finally:
        if not critical_error_occurred:
            result_str = (
                f"{email}:{password} [Added: {len(added_aliases)};"
                f" Aliases: {', '.join(added_aliases)}]"
                if added_aliases
                else f"{email}:{password} [Added: 0]"
            )
            log.info(f"[{email}] Finished. {result_str}")
            with output_lock:
                with settings.OUTPUT_FILE.open("a", encoding="utf-8") as file:
                    file.write(result_str + "\n")

        session.close()
        log.info(f"[{email}] Session closed.")
