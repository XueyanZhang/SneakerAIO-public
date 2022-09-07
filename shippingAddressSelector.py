# shopify
# https://shopify.dev/concepts/shopify-introduction
import requests
import json
import time
import profile
from logger import logger
from datetime import datetime


class ShopifyBot:
	profile = None
	session = None

	def __init__(self, profile_handle):
		self.profile = profile_handle
		self.session = self.init_session()

	def load_products(self) -> list:
		# return list of products
		url = f"{self.profile.BASE_URL}/products.json?limit=250&page=1"
		response = self.session.get(url)
		logger.info(f'Loading products: {response.status_code}')
		try:
			products = response.json()["products"]
			return products
			# print(products)
		except:
			logger.info(f'Website not compatible: {response.status_code}')
			exit(1)

	def locate_product(self, products) -> dict:
		# return the product with keywords
		# or None for not found
		keywords = self.profile.KEYWORDS
		num_keywords = len(keywords)
		logger.info(f'Searching for keywords: {";".join(keywords)}')
		# best_product = {'best_match': 0, 'product': None}
		for product in products:
			# print(json.dumps(product, indent=4))
			product_name = product["title"]
			# print(product_name)
			successful_match = 0
			for keyword in keywords:
				if keyword.lower() in product_name.lower():
					successful_match += 1
			if successful_match == num_keywords:
				logger.info(f'Product found: {product_name}')
				# print(json.dumps(product, indent=4))
				return product
			# if successful_match > best_product['best_match']:
			# 	best_product['best_match'] = successful_match
			# 	best_product['product'] = product
		logger.info('Prodcut not found')
		return None

	def stock_monitor(self) -> dict:
		# return the found product
		product = None
		count = 50  # cycles
		while not product:
			if count <= 1:
				logger.info(f'No product found after {count*self.profile.MONITOR_INTERVAL} seconds')
				exit(1)
			count -= 1
			products = self.load_products()
			product = self.locate_product(products)
			time.sleep(self.profile.MONITOR_INTERVAL)
		url_product = f'{self.profile.BASE_URL}/products/{product["handle"]}'
		logger.info(f'Product url: {url_product}')
		self.update_headers(url_product)
		# print(url_product)
		return product

	def select_size(self, product):
		# return variant id of the product
		# or None if not found
		size = self.profile.SIZE
		logger.info('Selecting size')
		variants = product['variants']
		for variant in variants:
			variant_title = variant['title']
			if size in variant_title:
				# print(f'{size} == {variant_title} ?')
				variant_id = variant['id']
				logger.info(f'{variant_title} selected -> size id: {variant_id}')
				return variant_id
		return None

	def add_to_cart(self, variant_id):
		# return cookies about added item
		url_cart = f'{profile.BASE_URL}/cart/add.js?quantity=1&id={variant_id}'
		response = self.session.get(url_cart)
		###
		self.record_response('addtocart.txt', response)
		###
		logger.info(f'Adding to cart: {response.status_code}')
		self.update_headers(url_cart)
		# print(json.dumps(response.json(), indent=4))
		try:
			cart_quantity = response.json()['quantity']  # quantity not accessible when failed to add
			cookies = response.cookies
			logger.info(f'Added: Quantity {cart_quantity}')
			return cookies
		except:
			logger.info('Failed to add')
			return None

	def get_checkout_link(self, cart_cookie) -> str:
		# https://shopify.dev/docs/admin-api/rest/reference/sales-channels/checkout
		url_checkout = f'{self.profile.BASE_URL}//checkout.json'
		response = self.session.get(url_checkout, cookies=cart_cookie)
		### test
		self.record_response('getcheckoutlink.txt', response)
		url_checkout = response.url
		return url_checkout

	def checkout_status(self, cart_cookie):
		url_checkout = self.get_checkout_link(cart_cookie)
		logger.info(f'Checkout url:\n{url_checkout}')
		count = 60
		while 'stock_problems' in url_checkout:
			if count <= 1:
				logger.warning(f'No restock after {count*self.profile.OPERATION_INTERVAL} seconds')
				return None
			count -= 1
			logger.info('Waiting for restock')
			time.sleep(self.profile.OPERATION_INTERVAL)
			url_checkout = self.get_checkout_link(cart_cookie)
		while 'queue' in url_checkout:
			logger.info('Waiting in queue')
			time.sleep(self.profile.OPERATION_INTERVAL)
		logger.info('Queue passed')
		# TODO: login if required
		# TODO: Captcha/reCaptcha if required
		self.update_headers(url_checkout)
		return url_checkout

	def submit_billing(self, url_checkout, cart_cookies):
		# <input name="authenticity_token" value="f2r...nTw==">
		authenticity = self.get_authenticity_token()
		payload = {
			"utf8": u"\u2713",
			"_method": "patch",
			"authenticity_token": authenticity,
			"previous_step": "contact_information",
			"step": "shipping_method",
			"checkout[email]": self.profile.EMAIL,
			"checkout[buyer_accepts_marketing]": "0",
			"checkout[shipping_address][first_name]": self.profile.FIRST_NAME,
			"checkout[shipping_address][last_name]": self.profile.LAST_NAME,
			"checkout[shipping_address][company]": self.profile.COMPANY,
			"checkout[shipping_address][address1]": self.profile.ADDRESS1,
			"checkout[shipping_address][address2]": self.profile.ADDRESS2,
			"checkout[shipping_address][city]": self.profile.CITY,
			"checkout[shipping_address][country]": self.profile.COUNTRY,
			"checkout[shipping_address][province]": self.profile.PROVINCE,
			"checkout[shipping_address][zip]": self.profile.ZIP,
			"checkout[shipping_address][phone]": self.profile.PHONE,
			"checkout[remember_me]": "0",
			"checkout[client_details][browser_width]": "1440",
			"checkout[client_details][browser_height]": "700",
			"checkout[client_details][javascript_enabled]": "1",
			"button": ""
		}
		response = self.session.post(url_checkout, cookies=cart_cookies, data=payload)
		### test
		self.record_response('response_records/submitbilling.txt', response)
		logger.info(f'Contact information: {response.status_code}')
		# logger.info(f'contact filled:\n{response.url}')
		return True

	def get_authenticity_token(self):
		return ''

	def get_shipping_token(self, cart_cookies):
		url_shipping = f'{self.profile.BASE_URL}//cart/shipping_rates.json?shipping_address[zip]={self.profile.ZIP}&shipping_address[country]={self.profile.COUNTRY}&shipping_address[province]={self.profile.PROVINCE}'
		response = self.session.get(url_shipping, cookies=cart_cookies)
		### test
		self.record_response('getshippingtoken', response)

		logger.info(f'Shipping information: {response.status_code}')
		try:
			shipping_options = response.json()
			# print(json.dumps(shipping_options, indent=4))
			default_option = shipping_options["shipping_rates"][0]
			name = default_option["name"].replace(' ', '%20')  # default shipping option
			price = default_option["price"]
			shipping_token = f'shopify-{name}-{price}'
			return shipping_token
		except:
			logger.info('Failed to submit shipping info')
			return None

	def get_payment_token(self, session):
		# https://shopify.dev/docs/admin-api/rest/reference/sales-channels/payment#create_payment_session-2021-01
		url_payment_token = "https://elb.deposit.shopifycs.com/sessions"
		payload = {
			'credit_card': {
				'number': self.profile.CARD_NUMBER,
				'first_name': self.profile.CARD_FIRST_NAME,
				'last_name': self.profile.CARD_LAST_NAME,
				'month': self.profile.CARD_EXP_MONTH,
				'year': self.profile.CARD_EXP_YEAR,
				'verification_value': self.profile.CARD_CVV
			}
		}
		response = session.post(url_payment_token, json=payload)  # json not data here.
		try:
			payload_id = response.json()['id']
			print(f'Payment id: {payload_id}')
			return payload_id
		except:
			print('Failed to get payment id')
			return None

	def login(self, session):
		url_login = f'{self.profile.BASE_URL}/account/login'
		payload = {
			'form_type': "customer_login",
			'utf8': "✓",
			'customer[email]': self.profile.EMAIL,
			'customer[password]': self.profile.PSWD,
			'return_url': '/account'
		}
		url_refer = f'{self.profile.BASE_URL}/login?return_url=%2Faccount'
		self.update_headers(url_refer)
		response = session.post(url_login, data=payload)
		logger.info(f'Logged in: {response.status_code}\nreturned url: {response.url}')
		# print(response.content)

	def init_session(self):
		# unspecious headers avoids blocking. requests default User-Agent: python-requests/2.25.1
		headers = {
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Safari/605.1.15',
			'Origin': self.profile.BASE_URL,
			'Referer': self.profile.BASE_URL,
			'Connection': 'keep-alive',
			'Accept-Language': 'en-US,en;q=0.5'
		}
		session = requests.session()
		session.headers.update(headers)
		return session

	def update_headers(self, url):
		headers = {
			'Referer': f'{url}'
		}
		self.session.headers.update(headers)

	def record_response(self, filename, response):
		#
		with open(f'./response_records/{filename}', 'a') as f:
			f.write(f'timestamp -> {datetime.now()}')
			f.write(f'status code: {response.status_code}\n')
			f.write(f'url: {response.url}\n')
			try:
				buf = json.dumps(response.json(), indent=4)
			except:
				buf = response.text
			f.write(buf)



def main():
	bot = ShopifyBot(profile)

	product = bot.stock_monitor()
	variant_id = bot.select_size(product)


	cookies = bot.add_to_cart(variant_id)
	url_checkout = bot.get_checkout_link(cookies)
	bot.submit_billing(url_checkout, cookies)
	bot.get_shipping_token(cookies)








if __name__ == "__main__":
	main()


# image src link
# images = product['images']
# try:
# 	imagesrc = images[0]['src']
# except:
# 	imagesrc = 'None'
# print(imagesrc)

# Test headers
# r = session.get('https://httpbin.org/headers')
# print(r.request.headers)
# print(r.text)





