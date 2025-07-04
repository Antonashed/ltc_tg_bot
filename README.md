# ltc_tg_bot
A simple free Telegram bot that can be used to sell products worldwide.

## Required environment variables

The bot uses symmetric encryption for storing wallet keys. Set the
`ENCRYPTION_KEY` environment variable before running the application. The value
must be a base64 encoded key compatible with `cryptography.Fernet`.
