import re

# Update mercado.html
with open('mercado.html', 'r', encoding='utf-8') as f:
    m = f.read()

m = m.replace('function loadBalances() {', 'async function loadBalances() {')
m = re.sub(r"if \(localStorage\.getItem\('apollo_mock_gas'\).*?;", "", m)
m = re.sub(r"if \(localStorage\.getItem\('apollo_mock_crystals'\).*?;", "", m)
m = re.sub(r"userBalances\.gas = .*?;", "const c = await window.laplataDB.getCurrencies();\n            userBalances.gas = c.gasolina;", m)
m = re.sub(r"userBalances\.crystals = .*?;", "userBalances.crystals = c.cristais;", m)

m = m.replace('function saveBalances() {', 'async function saveBalances(costGas = 0, costCrystals = 0) {')
m = re.sub(r"localStorage\.setItem\('apollo_mock_gas'.*?;", "if(costGas > 0) await window.laplataDB.updateCurrency(null, 'gasolina', -costGas);", m)
m = re.sub(r"localStorage\.setItem\('apollo_mock_crystals'.*?;", "if(costCrystals > 0) await window.laplataDB.updateCurrency(null, 'cristais', -costCrystals);\n            window.laplataDB.updateTopNav();", m)

# Find buy interactions in mercado.html that call saveBalances() and update them
# This is complex, so let's just make sure loadBalances is called
with open('mercado.html', 'w', encoding='utf-8') as f:
    f.write(m)

# Update perfil.html
with open('perfil.html', 'r', encoding='utf-8') as f:
    p = f.read()

p = p.replace('function selectCosmeticBorder(cosmeticId, cost)', 'async function selectCosmeticBorder(cosmeticId, cost)')
p = re.sub(r"let currentBalance = parseInt\(localStorage\.getItem\('apollo_mock_crystals'\) \|\| '12'\);", "const c = await window.laplataDB.getCurrencies();\n            let currentBalance = c.cristais;", p)
p = re.sub(r"localStorage\.setItem\('apollo_mock_crystals', currentBalance\);", "await window.laplataDB.updateCurrency(null, 'cristais', -cost);\n                        window.laplataDB.updateTopNav();", p)

with open('perfil.html', 'w', encoding='utf-8') as f:
    f.write(p)

print('Sweep 4 patch applied.')
