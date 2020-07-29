d<-read.csv("hh.csv",sep=';')
m<-as.matrix(d)
print( summary( m ) )
m[m>2]=2
jpeg('hell.jpg')
plot( as.raster(m[50:200,]/2))

#dev.off()

#matplot(m, type = c("l"),pch=1,cex=0.1)

