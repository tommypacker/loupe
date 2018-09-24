import rankr
from config import config


if __name__ == '__main__':
	app = rankr.create_app(config)
	app.run()