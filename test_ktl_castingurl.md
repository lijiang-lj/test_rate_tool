(process-rate-env) PS C:\Users\IAJ2WX\OneDrive - Bosch Group\code\test_rate_tool> python .\test_process_rate_multiprocess_cnyh.py
✅ 已加载 .env 文件: C:\Users\IAJ2WX\OneDrive - Bosch Group\code\test_rate_tool\.env
✅ 已启用代理: http://iaj2wx:18660826712Lj@rb-proxy-unix-szh.bosch.com:8080
[WARN] ⚠️ CSV 加载失败：[Errno 2] No such file or directory: 'C:\\Users\\IAJ2WX\\OneDrive - Bosch Group\\code\\test_rate_tool\\data\\process_rates.csv'

################################################################################
开始测试： Case 2：Casting 工艺 - 统一单位 (CNY/h)
################################################################################

================================================================================
🚀 工艺成本查询 - 完全由 LLM 推理
================================================================================
📍 地区: Ningbo, Zhejiang
🔧 工艺: Casting
🧱 材料: AlSi9Mn
📐 表面积: 3110.0 cm²
📊 体积: 195.6 cm³
📦 年产量: 1,100,000 件
💰 目标单位: CNY/h（自由字符串，无硬编码枚举）
================================================================================


[INFO] 📡 开始收集实时数据...
🔍 Tavily 查询: China Ningbo, Zhejiang manufacturing labor cost per hour 2025 CNY
🔍 Tavily 查询: China Ningbo, Zhejiang industrial electricity water natural gas price 2025
🔍 Tavily 查询: Casting process equipment cost depreciation manufacturing
🔍 Tavily 查询: Casting process energy consumption electricity water gas
[INFO] ✅ 实时数据收集完成

[INFO] 🧠 LLM 开始推理成本...
[INFO] ✅ LLM 推理完成


================================================================================
Case 2：Casting 工艺 - 统一单位 (CNY/h)
================================================================================
▶ final_cost: 621.51 CNY/h
▶ base_hourly_cost (CNY/h): 621.51
▶ csv_baseline: {}

🔍 full JSON:
{
  "query": {
    "location": "Ningbo, Zhejiang",
    "process_name": "Casting",
    "material_name": "AlSi9Mn",
    "surface_area_cm2": 3110.0,
    "volume_cm3": 195.6,
    "annual_volume": 1100000,
    "target_unit": "CNY/h"
  },
  "csv_baseline": {},
  "llm_reasoning": {
    "target_unit": "CNY/h",
    "material_density_g_per_cm3": 2.68,
    "calculated_weight_kg": 0.524,
    "processing_speed": {
      "value": 80,
      "unit": "pcs/h",
      "reasoning": "Assume high-pressure die casting (HPDC) of AlSi9Mn on an 800–1250 t cell with a single-cavity tool and typical cycle time ~45 s including shot, solidification, die open/close, spray, and part extraction. 3600 s/h ÷ 45 s ≈ 80 pcs/h. Note: To achieve 1.1 million pcs/year, a multi-cavity tool and/or multiple cells are required; however, our costing is per cell-hour."
    },
    "base_hourly_cost": {
      "labor_CNY_per_hour": 116.44,
      "energy_CNY_per_hour": 152.13,
      "depreciation_CNY_per_hour": 352.94,
      "total_CNY_per_hour": 621.51,
      "reasoning": "Labor: Direct operators: 2 persons × 30 RMB/h = 60 RMB/h. QC shared: 0.5 × 35 RMB/h = 17.5 RMB/h. Supervisor share: 0.25 × 50 RMB/h = 12.5 RMB/h. Maintenance share: 0.25 × 45 RMB/h = 11.25 RMB/h. Subtotal wages = 101.25 RMB/h. Add statutory/social contributions ~15% (assumption) → 101.25 × 1.15 = 116.44 RMB/h. Basis for wage assumptions: Ningbo hourly minimum 22 RMB/h (2023, Kinyu) and average monthly ~11,000 RMB/month (~63 RMB/h implies higher-skilled averages), so 30–50 RMB/h for shop-floor roles is reasonable. Energy: Part mass per piece = 195.6 cm³ × 2.68 g/cm³ = 524 g = 0.524 kg. Throughput = 80 pcs/h → melt rate ≈ 41.9 kg/h. Electric melting + holding assumed. Specific energy for aluminum melt + hold ≈ 1.3 kWh/kg (1.1 kWh/kg melt + 0.2 holding, assumption aligned with industry practice). Melting+holding electricity = 41.9 kg/h × 1.3 kWh/kg ≈ 54.47 kWh/h. HPDC machine hydraulics + servos average ≈ 120 kW over the cycle → 120 kWh/h. Die heating & ancillaries ≈ 15 kWh/h. Total electricity ≈ 54.47 + 120 + 15 = 189.47 kWh/h. Industrial electricity price in Zhejiang (assumption due to regionally differentiated TOU; typical range 0.55–0.85 RMB/kWh) set at 0.75 RMB/kWh → 189.47 × 0.75 = 142.13 RMB/h. Compressed air/water/auxiliary energy add ≈ 10 RMB/h (assumption). Energy total ≈ 142.13 + 10 = 152.13 RMB/h. Note: Foseco notes melting/holding/pouring often dominate foundry energy; HPDC cells also consume substantial hydraulic power, so share is more balanced. Depreciation: Assume a single 1250 t HPDC cell investment (die casting machine + furnace + ladle/robot + trim press + peripherals) ≈ 15,000,000 RMB (assumption from industry range; new large HPDC machines ~8–12M RMB and peripherals 5–10M RMB). Depreciation period 10 years, annual scheduled 5000 h, utilization 85% → effective hours/year = 5000 × 0.85 = 4250 h. Depreciation per hour = 15,000,000 ÷ (10 × 4250) = 352.94 RMB/h. Equipment price note:  未找到可靠的 1250t 东芝压铸机公开报价 URL; investment assumed from general industry ranges and experience; used solely for depreciation estimation."
    },
    "unit_conversion": {
      "from_unit": "CNY/h",
      "to_unit": "CNY/h",
      "conversion_factor": 1,
      "reasoning": "Target unit equals base unit. No physical conversion needed; cost per operating hour is directly reported."
    },
    "final_cost": 621.51,
    "final_unit": "CNY/h",
    "cost_breakdown": {
      "labor": 116.44,
      "energy": 152.13,
      "depreciation": 352.94
    },
    "detailed_reasoning": "Context and inputs: Region Ningbo, Zhejiang; process Casting (assumed HPDC for AlSi9Mn); material volume 195.6 cm³; area 3110 cm²; annual demand 1,100,000 pcs/year; target unit CNY/h. We build a CNY/h cell-hour cost: labor + energy + depreciation. 1) Material density and part mass: AlSi9Mn density taken as 2.68 g/cm³ (close to Al-Si die-cast alloys ~2.66–2.70). Weight = 195.6 × 2.68 = 524 g ≈ 0.524 kg. 2) Processing speed (pcs/h): Typical HPDC 800–1250 t cycle time for ~0.5 kg aluminum part is 35–60 s; we assume 45 s. Single cavity throughput 3600/45 ≈ 80 pcs/h. Note on annual volume: 1.1M pcs/year ÷ 80 pcs/h ≈ 13,750 h/year; hence real plants would use multi-cavity tools (e.g., 2–4 cavities) and/or multiple cells. Our costing is per cell-hour (independent of annual schedule). 3) Labor assumptions (Ningbo 2025): - Wage anchors: Ningbo minimum hourly wage ~22 RMB/h (2023, Kinyu: https://www.kinyu.co.uk/hiring-in-ningbo-labour-laws-salaries-and-best-practices/), Ningbo average salary ~11,000 RMB/month (~63 RMB/h at 8 h/day, 21.75 days/month), so operators typically ~25–35 RMB/h; QC/supervisors higher. - Staffing per cell-hour: 2 direct operators × 30 RMB/h (loading, spray, visual inspection, trim assist) = 60 RMB/h; QC shared 0.5 × 35 = 17.5 RMB/h; supervisor share 0.25 × 50 = 12.5 RMB/h; maintenance share 0.25 × 45 = 11.25 RMB/h. Subtotal 101.25 RMB/h. Add statutory/social contributions (pension/medical/unemployment, holiday, bonuses) estimated 15% → 116.44 RMB/h. This aligns with Ningbo manufacturing labor conditions, balancing minimum and average metrics. 4) Energy model: Die casting energy demand comprises melting/holding furnaces, hydraulics/servo drives, die heating/cooling, and auxiliaries (compressed air, water treatment). - Melt rate: 80 pcs/h × 0.524 kg = 41.9 kg/h. - Specific electricity for Al: melt ~1.1 kWh/kg, hold ~0.2 kWh/kg → total ~1.3 kWh/kg (industry typical; DOE/industry reports place aluminum electric melting ~0.7–1.3 kWh/kg depending on furnace; holding adds ~0.1–0.3). References context: DOE/ITP metalcasting energy studies and utility program literature discuss ranges (example program resource: https://assets.focusonenergy.com/production/inline-files/2024/2024-Metalcasting-Final.pdf; note: this document tabulates savings, not base intensities). Foseco overview indicates melting/holding/pouring often dominate foundry energy share (https://www.foseco.com/fileadmin/user_upload/images/about-us/sustainability/energy-efficient-casting_en.pdf), while HPDC hydraulics are substantial. - Melting+holding electricity = 41.9 × 1.3 ≈ 54.47 kWh/h. - HPDC machine hydraulics/servos avg load assumed 120 kW across cycle (large-tonnage HPDC machines often have installed hydraulics >200 kW with duty-cycle averaging 100–200 kW) → 120 kWh/h. - Die heating & ancillaries ~15 kWh/h. - Total electricity ≈ 189.47 kWh/h. - Electricity price: China industrial power rates are regionally differentiated with TOU; Zhejiang large industrial typical averages ~0.55–0.85 RMB/kWh; we assume 0.75 RMB/kWh (assumption due to lack of a precise posted Ningbo rate in the provided sources; see structure discussion: https://www.china-briefing.com/news/chinas-industrial-power-rates-category-electricity-usage-region-classification/). Electricity cost = 189.47 × 0.75 ≈ 142.13 RMB/h. - Aux energy (compressed air, water treatment, small gas burners if any): 10 RMB/h (assumption). Energy subtotal ≈ 152.13 RMB/h. Note: If natural gas-fired reverbs are used, gas price references: GlobalPetrolPrices shows March 2025 natural gas at ~0.049 USD/kWh (~0.36 RMB/kWh at 7.3 RMB/USD), and local historic Ningbo industrial gas ~3.42 RMB/m³ (CEIC: https://www.ceicdata.com/en/china/gas-price-36-city/cn-usage-price-natural-gas-for-industry-ningbo); switching furnace energy to gas would require furnace-specific efficiency and m³/kg factors (not applied here). 5) Equipment depreciation (HPDC cell): Requirement explicitly asks to consider die casting machine investment. We attempted to find a public price for a 1250 t Toshiba machine: 未找到可靠的 1250t 东芝压铸机公开报价 URL. Industry range and experience suggest a new 1000–1250 t HPDC machine ~8–12M RMB; peripherals (furnace, ladle/robot, trim press, automation, cooling, safety) ~5–10M RMB. We assume total cell investment 15,000,000 RMB solely for depreciation modeling (not a contract price). Depreciation period: 10 years (typical for heavy equipment). Annual scheduled hours: 5000 h (two shifts, maintenance downtime), utilization 85% → effective 4250 h/year. Hourly depreciation = 15,000,000 ÷ (10 × 4250) = 352.94 RMB/h. 6) Totals: Labor 116.44 RMB/h; Energy 152.13 RMB/h; Depreciation 352.94 RMB/h; Total 621.51 RMB/h. 7) Unit conversion: Target unit is CNY/h; same as base, conversion factor 1. If conversion to other units were required, we would use processing speed (pcs/h), volume rate (195.6 cm³ × 80 = 15,648 cm³/h), or mass rate (41.9 kg/h) to map CNY/h to CNY/pcs, CNY/cm³, or CNY/kg, respectively. 8) Scope and caveats: - Material cost, tooling amortization, consumables (release agents, shot sleeves), maintenance parts, quality testing, overhead, and scrap are excluded per requested split (labor, energy, depreciation). - Energy prices in China are TOU; actual costs vary by contract voltage level and time bands. - The assumed cycle time and cavity count materially impact unit (per-piece) costs but not the per-hour base cost structure. - The equipment investment is a non-binding assumption for modeling only. Sources referenced: labor context (https://www.kinyu.co.uk/hiring-in-ningbo-labour-laws-salaries-and-best-practices/); energy structure (https://www.china-briefing.com/news/chinas-industrial-power-rates-category-electricity-usage-region-classification/); natural gas context (https://www.globalpetrolprices.com/China/natural_gas_prices/, https://www.ceicdata.com/en/china/gas-price-36-city/cn-usage-price-natural-gas-for-industry-ningbo); foundry energy share overview (https://www.foseco.com/fileadmin/user_upload/images/about-us/sustainability/energy-efficient-casting_en.pdf); utility program resource on casting energy savings (https://assets.focusonenergy.com/production/inline-files/2024/2024-Metalcasting-Final.pdf)."
  },
  "final_cost": 621.51,
  "final_unit": "CNY/h",
  "base_hourly_cost": 621.51
}

################################################################################
开始测试： Case 5：KTL coating 工艺 - 统一单位 (CNY/h)
################################################################################

================================================================================
🚀 工艺成本查询 - 完全由 LLM 推理
================================================================================
📍 地区: Ningbo, Zhejiang
🔧 工艺: KTL coating
🧱 材料: AlSi9Mn
📐 表面积: 3110.0 cm²
📊 体积: 195.6 cm³
📦 年产量: 1,100,000 件
💰 目标单位: CNY/h（自由字符串，无硬编码枚举）
================================================================================


[INFO] 📡 开始收集实时数据...
🔍 Tavily 查询: China Ningbo, Zhejiang manufacturing labor cost per hour 2025 CNY
🔍 Tavily 查询: China Ningbo, Zhejiang industrial electricity water natural gas price 2025
🔍 Tavily 查询: KTL coating process equipment cost depreciation manufacturing
🔍 Tavily 查询: KTL coating process energy consumption electricity water gas
[INFO] ✅ 实时数据收集完成

[INFO] 🧠 LLM 开始推理成本...
[INFO] ✅ LLM 推理完成


================================================================================
Case 5：KTL coating 工艺 - 统一单位 (CNY/h)
================================================================================
▶ final_cost: 1081.1 CNY/h
▶ base_hourly_cost (CNY/h): 1081.1
▶ csv_baseline: {}

🔍 full JSON:
{
  "query": {
    "location": "Ningbo, Zhejiang",
    "process_name": "KTL coating",
    "material_name": "AlSi9Mn",
    "surface_area_cm2": 3110.0,
    "volume_cm3": 195.6,
    "annual_volume": 1100000,
    "target_unit": "CNY/h"
  },
  "csv_baseline": {},
  "llm_reasoning": {
    "target_unit": "CNY/h",
    "material_density_g_per_cm3": null,
    "calculated_weight_kg": null,
    "processing_speed": {
      "value": 229.0,
      "unit": "pcs/h",
      "reasoning": "Annual output is 1,100,000 pcs/year. Assume the KTL line operates 2 shifts of 8 h/day (16 h/day), 300 days/year, giving 4,800 h/year. Throughput = 1,100,000 pcs / 4,800 h ≈ 229 pcs/h. Each part has 0.311 m² surface area (3110 cm²), so area throughput ≈ 229 × 0.311 ≈ 71.3 m²/h. This aligns with a medium-size automotive KTL line handling small parts."
    },
    "base_hourly_cost": {
      "labor_CNY_per_hour": 273.5,
      "energy_CNY_per_hour": 350.1,
      "depreciation_CNY_per_hour": 457.5,
      "total_CNY_per_hour": 1081.1,
      "reasoning": "KTL line cost model in Ningbo, Zhejiang, split into labor, energy, and depreciation on a per-hour basis. Labor: Direct operators: 4 loaders/unloaders + 1 bath operator + 1 oven operator = 6 persons at 28 CNY/h each → 6 × 28 = 168 CNY/h. Indirect: 1 QC at 32 CNY/h → 32; 1 shift leader at 40 CNY/h → 40; 0.2 maintenance tech at 45 CNY/h → 9; 0.2 workshop manager at 60 CNY/h → 12; 0.5 assistant/admin at 25 CNY/h → 12.5. Total labor = 168 + 32 + 40 + 9 + 12 + 12.5 = 273.5 CNY/h. Wage assumptions are anchored by Ningbo minimum hourly wage of 22 CNY/h for part-time workers (Kinyu article) and typical manufacturing premiums; URL: https://www.kinyu.co.uk/hiring-in-ningbo-labour-laws-salaries-and-best-practices/. Energy: Use specific energy per processed area. Area throughput ≈ 71.3 m²/h. Electricity intensity (deposition rectifier, pumps, conveyors, compressed air): assume 2.0 kWh/m² (typical 1–3 kWh/m² for e-coat deposition and auxiliaries). Electricity use = 71.3 × 2.0 ≈ 142.6 kWh/h. Electricity tariff assumed 0.85 CNY/kWh (typical Zhejiang industrial TOU average per China Briefing context); cost ≈ 142.6 × 0.85 ≈ 121.2 CNY/h. Natural gas for curing ovens: assume 0.9 Nm³/m² (typical 0.6–1.2 Nm³/m² depending on oven load, temperature, insulation). Gas volume ≈ 71.3 × 0.9 ≈ 64.2 Nm³/h. Industrial gas price assumed 3.5 CNY/Nm³, referencing historical Ningbo industrial price 3.42 CNY/m³ (CEIC, Jul 2018: https://www.ceicdata.com/en/china/gas-price-36-city/cn-usage-price-natural-gas-for-industry-ningbo) and national 0.049 USD/kWh energy basis (GlobalPetrolPrices, Mar 2025: https://www.globalpetrolprices.com/China/natural_gas_prices/), consistent with ≈3.5 CNY/m³ assuming ≈10 kWh/Nm³. Gas cost ≈ 64.2 × 3.5 ≈ 224.7 CNY/h. Water: pretreatment and rinses ~10 L/m² → 0.71 m³/h; industrial water + wastewater ≈ 6 CNY/m³ → ≈ 4.3 CNY/h. Total energy ≈ 121.2 + 224.7 + 4.3 ≈ 350.1 CNY/h. Depreciation: KTL line capex assumed 20,000,000 CNY for a medium automotive line including pretreatment, KTL bath, ovens, racks, and water treatment (no reliable public price URL found for a full turnkey KTL line; made-in-china listings show systems but not transparent prices: e.g., https://m.made-in-china.com/product/Ktl-Painting-Electrocoating-Electrodeposition-Electrophoretic-Coating-System-E-Coat-Process-2056408532.html). Salvage value 10% → depreciable base 18,000,000 CNY over 10 years. Operating hours per year: 16 h/day × 300 days/year = 4,800 h/year; over 10 years → 48,000 h. Equipment depreciation per hour = 18,000,000 / 48,000 ≈ 375 CNY/h. Facility/space: footprint ≈ 1,500 m² for line + utilities. Rent assumed 22 CNY/m²/month in Ningbo industrial parks (typical range ~18–30); monthly rent 1,500 × 22 = 33,000 CNY. Operating hours approx 16 h/day × 25 days/month ≈ 400 h/month. Rent per operating hour ≈ 33,000 / 400 ≈ 82.5 CNY/h. Depreciation subtotal ≈ 375 + 82.5 = 457.5 CNY/h. Total base hourly cost = labor 273.5 + energy 350.1 + depreciation 457.5 ≈ 1,081.1 CNY/h."
    },
    "unit_conversion": {
      "from_unit": "CNY/h",
      "to_unit": "CNY/h",
      "conversion_factor": 1.0,
      "reasoning": "The target billing unit equals the base unit (CNY per hour). Therefore, no physical conversion is needed; conversion factor is 1."
    },
    "final_cost": 1081.1,
    "final_unit": "CNY/h",
    "cost_breakdown": {
      "labor": 273.5,
      "energy": 350.1,
      "depreciation": 457.5
    },
    "detailed_reasoning": "Process and context: KTL (cathodic dip coating, e-coat) involves aqueous paint deposition by DC power, followed by thermal curing. Pretreatment lines (degrease, rinse, phosphating), e-coat bath temperature control, rectifier, conveyors, and curing ovens (often gas-fired) dominate utilities. References for process description: Indufinish KTL (https://www.indufinish.com/en/ktl/), and general KTL system descriptions (e.g., made-in-china listing noting ovens may use gas or electricity: https://m.made-in-china.com/product/Ktl-Painting-Electrocoating-Electrodeposition-Electrophoretic-Coating-System-E-Coat-Process-2056408532.html). Geometry and throughput: Given part area 3110 cm² = 0.311 m²; volume 195.6 cm³ is not directly used for KTL costing. Annual volume is 1,100,000 pcs, implying required throughput ≈ 1,100,000 / (16 h/day × 300 d/year) ≈ 229 pcs/h, which yields area processed ≈ 71.3 m²/h. This area rate is realistic for a medium line handling small cast aluminum components. Energy model by area: E-coat rectifier and auxiliaries typically consume 1–3 kWh/m²; ovens typically consume 0.6–1.2 Nm³ NG/m² depending on cure temperature (160–180 °C), oven load factor, and insulation. Rinsing water consumption is often 5–15 L/m² depending on cascade stages; 10 L/m² (0.01 m³/m²) is a reasonable midpoint. With 71.3 m²/h: electricity ≈ 2 kWh/m² → 142.6 kWh/h; gas ≈ 0.9 Nm³/m² → 64.2 Nm³/h; water ≈ 0.01 m³/m² → 0.71 m³/h. Energy prices for 2025 Ningbo/Zhejiang context: - Natural gas: Historical Ningbo industrial tariff was 3.42 CNY/m³ (CEIC, Jul 2018: https://www.ceicdata.com/en/china/gas-price-36-city/cn-usage-price-natural-gas-for-industry-ningbo). National indicator in Mar 2025 shows NG energy price ≈ 0.049 USD/kWh (GlobalPetrolPrices: https://www.globalpetrolprices.com/China/natural_gas_prices/), which maps to ≈0.35 CNY/kWh at ~7.2 CNY/USD, and ≈3.5 CNY/m³ using 10 kWh/Nm³, consistent with the CEIC level. Assumption: 3.5 CNY/m³ in 2025. - Electricity: Industrial TOU rates in Zhejiang vary by voltage class and time bands; typical blended averages for medium-voltage users are ~0.8–1.0 CNY/kWh. Assumption here: 0.85 CNY/kWh. Context article: China Briefing, 2025 guide to industrial power rates (https://www.china-briefing.com/news/chinas-industrial-power-rates-category-electricity-usage-region-classification/). - Water + wastewater: Assumed at 6 CNY/m³ (typical industrial range 4–8 CNY/m³ including discharge fees in coastal provinces). Energy cost per hour: electricity ≈ 142.6 kWh/h × 0.85 ≈ 121.2 CNY/h; NG ≈ 64.2 m³/h × 3.5 ≈ 224.7 CNY/h; water ≈ 0.71 m³/h × 6 ≈ 4.3 CNY/h; total ≈ 350.1 CNY/h. Labor model based on workshop structure: Direct operators include loaders/unloaders, bath operator, and oven operator. Indirects include QC, shift leader, maintenance (fractional), manager (fractional), and assistant/admin. Hourly wage assumptions in Ningbo: operators at 28 CNY/h, QC at 32 CNY/h, shift leader at 40 CNY/h, maintenance at 45 CNY/h, manager at 60 CNY/h, assistant at 25 CNY/h. These sit above the local minimum hourly wage (22 CNY/h for part-time in Ningbo districts per Kinyu article: https://www.kinyu.co.uk/hiring-in-ningbo-labour-laws-salaries-and-best-practices/) and reflect manufacturing practice in 2025. Headcount per hour: - Direct: 4 loaders/unloaders + 1 bath operator + 1 oven operator = 6 persons → 6 × 28 = 168 CNY/h. - Indirect: QC 1 × 32 = 32; shift leader 1 × 40 = 40; maintenance 0.2 × 45 = 9; manager 0.2 × 60 = 12; assistant 0.5 × 25 = 12.5; subtotal indirect = 105.5; total labor ≈ 273.5 CNY/h. Depreciation model: - KTL line capex assumption: 20,000,000 CNY for a medium automotive line including pretreatment tanks, heaters, filtration, e-coat bath with rectifier, conveyors, curing ovens, racks, water treatment, and basic automation. Public turnkey prices are not readily disclosed by suppliers; made-in-china listings show systems but no transparent prices (example: https://m.made-in-china.com/product/Ktl-Painting-Electrocoating-Electrodeposition-Electrophoretic-Coating-System-E-Coat-Process-2056408532.html). Statement: 未找到可靠的完整KTL产线公开报价URL；因此采用行业常识的区间假设。 Typical ranges for automotive-quality KTL lines in China are roughly mid- to high-single-digit millions up to several tens of millions of CNY depending on scale; 20M is a reasonable midpoint for a medium line. - Salvage value assumed 10% (2,000,000 CNY), depreciable base 18,000,000 CNY. Depreciation method: straight-line over 10 years; operating hours 16 h/day × 300 days/year = 4,800 h/year; total 48,000 h over 10 years. Equipment depreciation per operating hour ≈ 18,000,000 / 48,000 ≈ 375 CNY/h. - Facility/space cost: footprint ≈ 1,500 m²; rent assumed 22 CNY/m²/month. Monthly rent ≈ 33,000 CNY. Operating hours ≈ 400 h/month (16 h/day × ~25 days). Rent per operating hour ≈ 33,000 / 400 ≈ 82.5 CNY/h. We roll this into depreciation category to keep the requested three-field structure. Depreciation subtotal ≈ 375 + 82.5 = 457.5 CNY/h. Total base hourly cost = labor (273.5) + energy (350.1) + depreciation (457.5) ≈ 1,081.1 CNY/h. Additional items not included in base (not requested in the three-field split but relevant for quotations): - Paint/chemicals consumption: e-coat paint solids typically 8–15 g/m²; at 71.3 m²/h this is ~0.57–1.07 kg/h of paint solids, plus losses and replenishment; paint cost can be substantial (e.g., 30–60 CNY/kg for certain e-coats), potentially adding 20–60 CNY/h depending on system solids and loss. - Maintenance/fixtures: racks, caps, hooks, and periodic refurbishment often add 0.1–0.5 CNY/pcs; at 229 pcs/h this could be ~23–115 CNY/h. - Wastewater treatment chemicals and sludge disposal could add ~5–20 CNY/h depending on load. - QC lab testing: periodic salt spray, adhesion, thickness checks are usually batch costs and can be amortized over output; often small per hour. - Overhead/management charge: commonly applied as a percentage (e.g., 10–25%) over direct costs to cover administrative, compliance, and risk; for transparency, we have not applied it in the base hourly cost, but a typical workshop quote might add ~15% to account for RMOC/risk. - Scrap: KTL scrap rate typically 1–3% with stable pretreatment; assumed 2% as a planning figure. For hourly costing, scrap impacts material and rework more than the three base categories. Unit conversion: Target unit is CNY/h; conversion factor from base CNY/h is 1. If conversion to other units were needed (e.g., CNY/pcs or CNY/m²), one would divide by throughput (pcs/h or m²/h). For example, CNY/pcs ≈ 1,081.1 / 229 ≈ 4.72 CNY/pcs excluding paint/consumables and overhead; CNY/m² ≈ 1,081.1 / 71.3 ≈ 15.2 CNY/m². Assumptions and limitations: - Wages are assumed based on Ningbo context; actual enterprise rates vary by skill and benefits. - Electricity tariff is assumed; actual TOU tariffs and voltage class can materially change energy costs. - Gas price is triangulated from CEIC and national indicators; local contract prices may differ. - Energy intensities per m² are typical ranges; specific line designs, bath chemistries, oven efficiencies, and load factors cause variance. - Capex and footprint are assumed; real KTL lines may differ substantially in investment and space. - The model intentionally does not allocate 100% of annual depreciation to a single product; depreciation is per operating hour, which is equitable across multi-project utilization. Overall, the 1,081.1 CNY/h base is physically and economically consistent for a medium-sized KTL line in Ningbo handling small aluminum castings."
  },
  "final_cost": 1081.1,
  "final_unit": "CNY/h",
  "base_hourly_cost": 1081.1
}
(process-rate-env) PS C:\Users\IAJ2WX\OneDrive - Bosch Group\code\test_rate_tool> 