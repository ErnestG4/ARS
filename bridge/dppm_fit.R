# BRIDGE-B: spatstat DPP + cluster fits on an exported point set.
# Usage: Rscript dppm_fit.R points.csv window.csv out_prefix rmax
# Fits dppGauss, dppCauchy, dppMatern, dppPowerExp (minimum contrast on pcf),
# plus Thomas (kppm) as the clustered alternative.  Emits:
#   <pre>_params.csv  (model, param, value)
#   <pre>_gmodel.csv  (model, r, g)   — model pcf curves for uniform python-side contrast
suppressMessages(library(spatstat))
args <- commandArgs(trailingOnly = TRUE)
pts <- read.csv(args[1]); w <- read.csv(args[2]); pre <- args[3]; rmax <- as.numeric(args[4])
if (w$type == "rect") {
  W <- owin(c(w$x0, w$x1), c(w$y0, w$y1))
} else if (w$type == "disk") {
  W <- disc(radius = w$R, centre = c(0, 0))
} else {
  th <- seq(w$t1, w$t2, length.out = 200)
  xs <- c(w$R1 * cos(th), rev(w$R2 * cos(th)))
  ys <- c(w$R1 * sin(th), rev(w$R2 * sin(th)))
  W <- owin(poly = list(x = rev(xs), y = rev(ys)))
}
X <- ppp(pts$x, pts$y, window = W)
rg <- seq(0.01, rmax, by = rmax / 200)
prm <- data.frame(); gmod <- data.frame()
fit_one <- function(name, expr) {
  fit <- tryCatch(expr, error = function(e) { cat("FIT FAIL", name, ":", conditionMessage(e), "\n"); NULL })
  if (is.null(fit)) return(invisible(NULL))
  p <- parameters(fit)
  for (k in names(p)) if (is.numeric(p[[k]]) && length(p[[k]]) == 1)
    prm <<- rbind(prm, data.frame(model = name, param = k, value = as.numeric(p[[k]])))
  gc <- tryCatch(pcfmodel(fit)(rg), error = function(e) rep(NA, length(rg)))
  gmod <<- rbind(gmod, data.frame(model = name, r = rg, g = gc))
  cat("fitted", name, "\n")
}
fit_one("dppGauss",    dppm(X ~ 1, dppGauss,    method = "mincon", statistic = "pcf", rmax = rmax))
fit_one("dppCauchy",   dppm(X ~ 1, dppCauchy,   method = "mincon", statistic = "pcf", rmax = rmax))
fit_one("dppMatern",   dppm(X ~ 1, dppMatern,   method = "mincon", statistic = "pcf", rmax = rmax))
if (Sys.getenv("SKIP_POWEREXP") != "1") fit_one("dppPowerExp", dppm(X ~ 1, dppPowerExp, method = "mincon", statistic = "pcf", rmax = rmax))
fit_one("Thomas",      kppm(X ~ 1, "Thomas",    statistic = "pcf", rmax = rmax))
write.csv(prm, paste0(pre, "_params.csv"), row.names = FALSE)
write.csv(gmod, paste0(pre, "_gmodel.csv"), row.names = FALSE)
cat("dppm_fit done: n =", npoints(X), "\n")
