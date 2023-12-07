library(ggplot2)
library(dplyr)

df_og = data.frame(corp_type = 'original',
                   auc = 36.42804556004095,
                   ave_dep = 81.39736684619989)
df_cf = data.frame(corp_type = 'counterfactual',
                   auc = 41.97718308652536,
                   ave_dep = 82.22095808383233)
ildl = rbind(df_og, df_cf)
print(ildl)
ildl %>% ggplot(aes(x=corp_type, y=auc)) +
  geom_bar(stat='identity', width=0.5) + 
  xlab('corpus type') +
  ylab('IL')
plot()
ildl %>% ggplot(aes(x=corp_type, y=ave_dep)) +
  geom_bar(stat='identity', width=0.5) + 
  xlab('corpus type') +
  ylab('DL')
plot()


# Plotting average surprisals by n in n-gram
cutoff = 4
df_og = data.frame(corp_type = rep('original', cutoff),
                 n = seq.int(0, cutoff-1),
                 surp = c(7.124277195811827, 5.523533054958732, 5.161046254724763, 5.101245235194012))
df_cf = data.frame(corp_type = rep('counterfactual', cutoff),
                   n = seq.int(0, cutoff-1),
                   surp = c(7.154441460467917, 6.078836177619852, 5.98183552451518, 5.98183552451518))

surps = rbind(df_og, df_cf)
print(surps)
surps %>% ggplot(aes(x=n, y=surp, group=corp_type, color=corp_type)) + 
  geom_point() +
  geom_line() +
  xlab('cutoff') + 
  ylab('average surprisal')
plot()

data = read.csv('results/results.csv', header = FALSE)
print(nrow(data))
print(ncol(data))
