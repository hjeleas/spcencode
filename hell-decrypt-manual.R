library(pracma)
p=3
h = ((1+hadamard(8))/2) %% p

hinv = matrix( c( 0.,1.,1.,1.,1.,1.,1.,1.,
1.,2.,1.,2.,1.,2.,1.,2.,
1.,1.,2.,2.,1.,1.,2.,2.,
1.,2.,2.,1.,1.,2.,2.,1.,
1.,1.,1.,1.,2.,2.,2.,2.,
1.,2.,1.,2.,2.,1.,2.,1.,
1.,1.,2.,2.,2.,2.,1.,1.,
1.,2.,2.,1.,2.,1.,1.,2. ),nrow=8)

d<-read.csv("hell.csv", sep=';')  
m<-as.matrix(d)
print( summary( m ) )

#e<-c(1,2,1,0,2,1,0,0)
#e<-c(0,1,1,0,2,1,1,2)
e<-rep( 0,8)

# 'normalize' matrix (in range p) 
for (i in seq(8)) {
 m[,i] = (   trunc(((p) * ( m[,i])/(1+max(m[,i])))) ) %% p
}
#matplot(m, type = c("l"),pch=1,cex=0.1)

# decrypt using inverse modular matrix
n = matrix( rep(0,8), ncol=8)
for (j in seq(nrow(m))) {
 n <- rbind(n, dot(  hinv ,   (m[j,] + p -e)%%p ) %% p ) 
}
summary(n)

plot( as.raster((n[50:150,]/3)))

