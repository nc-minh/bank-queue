order-service::
	python3 order-service/app.py  

payment-service::
	python3 payment-service/app.py  

restaurant-service::
	python3 restaurant-service/app.py  

delivery-service::
	python3 delivery-service/app.py  

queue::
	python3 queue/app.py  

init_db::
	python3 db/init_db.py



.PHONY: order-service payment-service restaurant-service delivery-service queue init_db