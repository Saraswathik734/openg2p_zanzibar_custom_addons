# openg2p-pbms-gen2
New Version of PBMS with a decoupled Eligibility and Entitlement Engine


## Docker Setup 
### Install postgres and expose port

````
docker run -d \
  --name db \
  --network odoo-network \
  -p 5433:5432 \
  -e POSTGRES_USER=odoo \
  -e POSTGRES_PASSWORD=odoo \
  -e POSTGRES_DB=postgres \
  postgres:15
  ````
  
### Install odoo with addons
````
docker run -d \
  --name odoo \
  --network odoo-network \
  -p 8069:8069 \
  -e HOST=db \
  -e USER=odoo \
  -e PASSWORD=odoo \
  -v /home/<path-to-odoo-conf>/odoo.conf:/etc/odoo/odoo.conf \
  -v /home/<path-to-odoo-conf>/odoo-addons:/mnt/extra-addons \
  odoo:17
````

## Debugging


### Remove pycache
````
docker exec -it odoo bash -c "find /mnt/extra-addons/ -name '__pycache__' -exec rm -rf {} +"
````

### Docker odoo shell

````
odoo shell --db_host=db  -r odoo -w odoo -d odoo
````