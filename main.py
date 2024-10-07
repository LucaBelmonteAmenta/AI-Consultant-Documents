from frontend.home import Home

class Main:
    @staticmethod
    def run():
        try:
            app = Home()
            app.run()
        except Exception as e:
            print(str(e))

if __name__ == '__main__':
    Main.run()




