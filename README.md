# Philippine PV Retirement Data and Code
Version 1.0. Release date 21 November 2026.

## Reproduction
With Python 3.12, install the versions in requirements.txt and run the following in this directory.

```sh
python -m pip install -r requirements.txt
OPENBLAS_NUM_THREADS=1 python reproduce.py
```

The run reads the two CSV inputs in data/ and writes results/ from scratch. The Python scripts generate the annual retirement series, provincial projections, all 3,000 parameter draws and their outcomes, rank coefficients, project assignments, lifetime and ordering experiments, reference curves, six numerical LaTeX tables and five PDF graphs. The two remaining figures are drawn directly by TikZ in the manuscript. The appendix parameter table lists the inputs used by the code. Project schedules are feasible incumbents with numerical objective bounds. Different solver builds or wall-time limits can select different assignments with similar objective values. Compare achieved annual MW and objective gaps as well as tonnage. The release schedules and numerical outputs are included. Regional labels 0, 1 and 2 denote Luzon, Visayas and Mindanao respectively. Monetary costs and measured retirement events are outside these data.

## Input registers
- Operating plants come from the Department of Energy grid-connected lists of 28 February 2025: [Luzon](https://prod-cms.doe.gov.ph/documents/d/epimb/01-luzon-grid-as-of-february-2025-pdf), [Visayas](https://prod-cms.doe.gov.ph/documents/d/epimb/02-visayas-grid-as-of-february-2025-pdf), [Mindanao](https://prod-cms.doe.gov.ph/documents/d/epimb/03-mindanao-grid-as-of-february-2025-pdf). Use the installed-capacity field. Retain ground-mounted plants with at least 1 MW. Commercial-operation/commissioning years use the earliest listed year when multiple phase dates share one capacity. The Sta. Rita rows use Zambales, and Cayanga-Bugallon uses Pangasinan. The list yields 48, 13 and 6 plants, totaling 2,221.77, 505.50 and 83.80 MWdc.
- Project awards come from the DOE [awarded Certificate of Authority register](https://prod-cms.doe.gov.ph/documents/d/guest/awarded-coa-2024-2025-pdf). The solar award identifier, province, model island group and potential MW are the input fields. Retain solar awards dated 2025 with potential capacity at least 1 MW and exclude entries described as rooftop or roof-mounted. Province labels reproduce the register except that wrapped multi-province text is joined. The central analysis uses the potential MW as MWdc. The island counts are 48, 27 and 23 and their capacities sum to 9,244.012 MW. Each identifier appears once. Separate DOE award identifiers are the smallest divisible administrative units in the whole-project experiment; each is assigned to one commissioning year or left unbuilt.
- Plant dates and award sizes describe installed/awarded capacity. The age-dependent removal curves, completion fractions, island multipliers and truck assumptions are scenarios. They do not document observed removal events, grant commitments or logistics contracts.

## Outputs
annual.csv contains the central series by stream, province.csv the operating plants' province-by-year mass, and province2035.csv both 2035 estimates. The calendar and lifetime experiments use tonnes and MW before rounding. In ordering.csv the swap direction moves the 2027 installation to Mindanao and the 2029 installation to Luzon. For the whole-project experiment, schedules.csv gives each award's year or zero for unbuilt. project-bounds.csv records the feasible objective, the continuous endpoint evaluated at the achieved annual margins, and the solver objective gap. simulations.csv pairs each independent input draw with four outputs; the seed is 20261121. The project is not dependent on external web access after the data and Python dependencies are present.
