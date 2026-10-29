# Open Source BUNKER online game
## Instructions

## Docker
- Stop and delete all containiers and volumes:
```
docker compose down -v
```
- Start all containers:
```
docker compose up -d
```

## PostgreSQL 

- Seed tables with data from scripts/data folder:
```
docker compose exec web python scripts/seed_db.py 
```

- CLI in/out:
```
docker exec -it bunker_postgres psql -U root -d bunker_db

\q
```

- All tables:
```
\dt
```

- Select all from table:
```
SELECT * FROM hobby;
```



