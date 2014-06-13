import imaplib
import click


@click.command()
@click.option("--u")
@click.option("--p")
def main(u,p):
	mail = imaplib.IMAP4_SSL('inn.innovareinternets.com.au')
	print mail.login(u,p)
	print mail.list()

if __name__ == "__main__":
	main()
