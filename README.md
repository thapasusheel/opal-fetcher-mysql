# Opal Fetcher MySQL

This custom data fetcher for OPAL allows you to get real-time data from MySQL databases. It supports flexible queries and easily integrates with OPAL for policy checks and decisions.

## Features:

- **Real-Time Data**: Quickly fetch data from MySQL databases.
- **Flexible Queries**: Use any query you need to get the right data.
- **Easy Integration**: Works smoothly with OPAL.
- **Better Decisions**: Access up-to-date data for informed decisions.

This fetcher connects MySQL databases with OPAL, ensuring you have the latest information for policy enforcement and decision-making.

## Installation

1. Install the [docker](https://www.docker.com/) in your machine.

2. Run the docker compose file

   ```bash
   sudo docker compose up --build
   ```

3. Head over to `http://localhost:7002` where server is hosted, and `http://localhost:7766` where client is running.
