# GPEA: A Green Pixel Engine for Analysis (and its derivatives, the \*ureka family)

## Overview

The GPEA, GPEureka, and Otsureka algorithms are algorithms designed to measure the 
growth rate of plants using overhead cameras (a color camera for the GPEA
algorithm, and an infrared camera for the GPEureka and Otsureka algorithms).

Their inner workings are documented in [paper.ipynb](https://github.com/colewebb/gpea/blob/main/paper.ipynb).
I haven't written up the Otsureka variant yet, but it's the GPEureka algorithm 
with Otsu's binarization applied instead of a static value.
