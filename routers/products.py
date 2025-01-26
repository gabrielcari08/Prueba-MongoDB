from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/products", 
                    tags=["products"],
                   responses={404: {"message": "No se ha encontrado"}})

products_list = ["Producto 1", "Producto 2", "Producto 3", "Producto 4", "Producto 5"]

@router.get("/")
async def get_all_products(): 
    return products_list

@router.get("/{id}")
async def get_product_by_id(id: int): 
    if id < 0 or id >= len(products_list):
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return products_list[id]
