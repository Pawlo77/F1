# F1
End-to-end project serving ETL and BI for F1-centered data,  part of IAD study program at Faculty of Mathematics and Information Science, Warsaw University of Technology

# Deployment of Data Warehouse

With local .env file created containing
```bash
PREFECT_CLOUD_API_KEY=
PREFECT_CLOUD_WORKSPACE=
REPO_URL=
REPO_TOKEN=
DB_HOST=
DB_PORT=
DB_DATABASE=
DB_USERNAME=
DB_PASSWORD=
```

In poetry home run `poetry run deploy && poetry run prefect deploy --all` after starting prefect server and making sure connection to database works.

# Local run for prefect

```bash
prefect server start

# in diferent terminal
prefect worker start --pool 'default-work-pool'
```

# Local run of flows

For example for entire elt process for Racing Circuits:
```
clear && poetry run python -m src.f1.flows.racing_circuits.elt
```

# Visualization

Example visualization is available via Power BI, source code is [here](./src/f1/reports/raport.pbix), with visualisation [here](./src/f1//reports/raport.pdf)

# Documentation

Entire project documentation and scope is available via polish PDF [here](./docs/report.pdf)
