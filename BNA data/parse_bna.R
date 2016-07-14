library(dplyr)
library(xml2)

files = c('XML/2000-2004.xml', 'XML/2005-2009.xml', 'XML/2010-2014.xml', 'XML/2015-2016.xml')

dataf = data.frame()

for (file in files) {
	readdata = read_xml(file)
	items = readdata %>% xml_find_all('//item')
	
	parse = function (item) {
		children = xml_children(item)
		names = xml_name(children)
		values = xml_text(children)
		df = matrix(values, nrow = 1) %>% as.data.frame(stringsAsFactors = FALSE)
		
		names(df) = names
		return(df)
	}
	file_df = lapply(items, parse) %>% do.call(rbind, .)
	file_df$description = gsub('\n', '', file_df$description)
	dataf = rbind(dataf, file_df)
}

write.csv(dataf, 'CSV/BNA.csv')
