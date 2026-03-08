import requests
import json
import os
import time

def test_seed_mode():
    url = "http://localhost:8888/run"
    
    # Valid image URL (Dummy Image)
    valid_img_url = "https://dummyimage.com/600x400/000/fff.jpg"
    
    payload_true = {
        "messages": [
            {
                "role": "human",
                "content": f"生成一张营销图。商品: 法式连衣裙, 店铺: 某某女装, 价格: 299. 图片: {valid_img_url}"
            }
        ],
        "seed_mode": "true"
    }
    
    # payload_false = {
    #     "messages": [
    #         {
    #             "role": "human",
    #             "content": f"生成一张营销图。商品: 法式连衣裙, 店铺: 某某女装, 价格: 299. 图片: {valid_img_url}"
    #         }
    #     ],
    #     "seed_mode": "false"
    # }
    
    print("Testing seed_mode='true'...")
    try:
        resp = requests.post(url, json=payload_true, timeout=600)
        print(f"Status: {resp.status_code}")
        res_json = resp.json()
        print(json.dumps(res_json, indent=2, ensure_ascii=False))
        
        # Check generated_image_urls
        urls = res_json.get("generated_image_urls", [])
        order_urls = res_json.get("generated_order_urls", [])
        
        print(f"Image URLs: {urls}")
        print(f"Order URLs: {order_urls}")
        
        if order_urls:
            print(f"SUCCESS: seed_mode='true' generated order cards in generated_order_urls: {order_urls}")
        else:
            print("FAILURE: seed_mode='true' did NOT generate order cards in generated_order_urls.")
            
    except Exception as e:
        print(f"Error: {e}")

    # print("\nTesting seed_mode='false'...")
    # try:
    #     resp = requests.post(url, json=payload_false, timeout=600)
    #     print(f"Status: {resp.status_code}")
    #     res_json = resp.json()
        
    #     # Check generated_image_urls
    #     urls = res_json.get("generated_image_urls", [])
    #     order_cards = [u for u in urls if "order_" in u]
    #     if not order_cards:
    #         print(f"SUCCESS: seed_mode='false' did NOT generate order cards.")
    #     else:
    #         print(f"FAILURE: seed_mode='false' generated order cards: {order_cards}")
            
    # except Exception as e:
    #     print(f"Error: {e}")

if __name__ == "__main__":
    test_seed_mode()
