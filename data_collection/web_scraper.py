from bs4 import BeautifulSoup
import requests
import urllib
import re
import json
import time
import datetime



def get_soup_from_page():
	html = requests.get("http://www.aire.cdmx.gob.mx/ultima-hora-reporte.php")
	return BeautifulSoup(html.text, "html.parser")


def get_dict_for_each_tr(trs):
	dict_res = []

	for tr in trs:
		tmp_res = {}
		tds = tr.find_all("td")
		if len(tr.find_all("td")) == 0:
			continue
		tmp_res["clave"] = tds[0].text
		tmp_res["alcaldia"] = tds[1].text
		tmp_res["calidad"] = tds[2].text
		tmp_res["contaminante"] = tds[3].text

		str_indice = tds[4].text
		if str_indice != '':

			semi_substr = re.sub(r'document\.write\(unescape\(\'.*(\n|\\n)<script type=\"text\/javascript\">(\n|\\n)document\.write\(\'', '', urllib.parse.unquote(str_indice))
			substr = re.sub(r'\'\)(\n|\\n)<\/script>(\n|\\n)?\'\)\)', '', semi_substr)
		else:
			substr = '0'

		tmp_res["indice"] = int(substr)
		dict_res.append(tmp_res)

		print("Clave: {}, Alcaldìa: {}, Calidad: {}, Contaminante: {}".format(tmp_res["clave"], tmp_res["alcaldia"], tmp_res["calidad"], tmp_res["contaminante"]))

	return dict_res


def save_results(dict_res, result_file):
	result_file = "{}_{:%d-%m-%Y_%H-%M}.json".format(result_file, datetime.datetime.now())
	with open(result_file, 'w', encoding="utf8") as fp:
		json.dump(dict_res, fp, ensure_ascii=False)
		print("Saved to {}".format(result_file))


def get_table_data(soup, id, file):
	table_rows = soup.body.find(id=id).table.find_all("tr")
	table_rows = table_rows[2:]  # delete HEADER CDMX and HEADERS TITLE COLUMNS

	dict_res = get_dict_for_each_tr(table_rows)

	save_results(dict_res, file)


def main():
	soup = get_soup_from_page()

	print("Getting tabladf...")
	get_table_data(soup, "tabladf", "tabladf")

	print("Getting tablaedomex...")
	get_table_data(soup, "tablaedomex", "tablaedomex")


if __name__ == "__main__":

	while True:
		main()
		print("\nEjecutando prueba",datetime.datetime.now())
		time.sleep(3600)

