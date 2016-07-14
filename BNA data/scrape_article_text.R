library(dplyr)
library(xml2)

dataf = read.csv('BNA.csv', stringsAsFactors = FALSE)
#dataf = dataf[2001:2113,]

gettext = function (url) {
    print(url)
    byline = NA
    text = NA
    parsed = read_xml(url, as_html = TRUE, verbose = TRUE)
    byline = parsed %>% xml_find_first('//div[@class="byline "]') %>% xml_text() %>%
        gsub('By ', '', .)
    if (length(byline) == 0) {
        byline = NA
    }
    pars = parsed %>% xml_find_all('//div[@class="p "]') %>% sapply(xml_text) %>% 
            paste(sep = '', collapse = '\n\n')
    return(data.frame(byline = byline, text = pars, stringsAsFactors = FALSE))
}

tempdf = lapply(dataf$link, gettext) %>% do.call(rbind, .)
dataf = cbind(dataf, tempdf)

write.csv(dataf, file = 'BNA.text.csv', fileEncoding = 'utf8')
