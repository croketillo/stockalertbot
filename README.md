
# Telegram Stock Price Alert Bot

This project is a Telegram bot that allows users to set up stock price alerts. The bot uses Yahoo Finance to get real-time stock prices and notifies users when their target price is reached.

## Features

- Set alerts for stock prices to notify when they go above or below a specified target.
- View current alert configurations.
- Remove existing alerts.
- Persistent storage of alert configurations using a JSON file.

## Requirements

- Docker
- Docker Compose

## Quick a easy Deployment

### 1. Clone the Repository

```sh
git clone https://github.com/your-username/telegram-stock-alert-bot.git
cd telegram-stock-alert-bot
```

### 2. Edit a `sample.env` File

Edit sample.env and type ypur telegram token. and your bot password (and rename the file ".env")

```sh
TELEGRAM_TOKEN=your-telegram-bot-token
BOT_PASSWORD=your_bot_password_here
```

### 3. Deploy the Docker Container

Use the provided `deploy.sh` script to build and deploy the container:

```sh
./deploy.sh
```

This will build the Docker image and start the container in detached mode.

### 4. Stop and Remove the Docker Container

To stop and remove the Docker container, use the provided `delete.sh` script:

```sh
./delete.sh
```

## Usage

### Commands

- **/start**: Welcome message and usage instructions.
- **/help**: Help message with usage instructions.
- **/set <TICKER> <TARGET PRICE> <UP/DOWN>**: Set an alert for a stock ticker at the target price in the specified direction (UP or DOWN).
- **/config**: View the current alert configurations.
- **/remove <TICKER>**: Remove the alert for the specified stock ticker.

### Examples

- Set an alert: `/set AAPL 150.00 UP`
- View current configurations: `/config`
- Remove an alert: `/remove AAPL`

## Logs

The bot logs its activity to `stocks_bot.log`. You can view the log file to monitor the bot's activity and debug issues.

## License

This project is licensed under the GNUv3 License. See the [LICENSE](LICENSE) file for details.

## Maintainer

Maintained by [CROKETILLO](mailto:croketillo@gmail.com).
