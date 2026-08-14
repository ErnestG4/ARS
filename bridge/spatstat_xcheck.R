# Observer-B cross-check: spatstat Kest/pcf on an exported point set.
# Usage: Rscript spatstat_xcheck.R points.csv window.csv out_prefix rmax
#   window.csv: one row; type=rect,x0,x1,y0,y1 | type=disk,R | type=wedge,R1,R2,t1,t2
# Emits <out_prefix>_K.csv (r, K_border, K_iso, K_trans) and <out_prefix>_g.csv (r, g_iso).
suppressMessages(library(spatstat))
args <- commandArgs(trailingOnly = TRUE)
pts <- read.csv(args[1]); w <- read.csv(args[2]); pre <- args[3]; rmax <- as.numeric(args[4])
if (w$type == "rect") {
  W <- owin(c(w$x0, w$x1), c(w$y0, w$y1))
} else if (w$type == "disk") {
  W <- disc(radius = w$R, centre = c(0, 0))
} else {  # wedge: polygonal approximation of the annular sector
  th <- seq(w$t1, w$t2, length.out = 200)
  xs <- c(w$R1 * cos(th), rev(w$R2 * cos(th)))
  ys <- c(w$R1 * sin(th), rev(w$R2 * sin(th)))
  W <- owin(poly = list(x = rev(xs), y = rev(ys)))
}
X <- ppp(pts$x, pts$y, window = W)
r <- seq(0, rmax, by = rmax / 100)
K <- Kest(X, r = r, correction = c("border", "isotropic", "translate"))
write.csv(data.frame(r = K$r, K_border = K$border, K_iso = K$iso, K_trans = K$trans),
          paste0(pre, "_K.csv"), row.names = FALSE)
g <- pcf(X, r = r, correction = "isotropic", divisor = "d")
write.csv(data.frame(r = g$r, g_iso = g$iso), paste0(pre, "_g.csv"), row.names = FALSE)
cat("spatstat xcheck done: n =", npoints(X), " lambda =", intensity(X), "\n")
