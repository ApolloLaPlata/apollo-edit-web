import { createCharacterMatchRegex } from './services/geminiService';
const regex = createCharacterMatchRegex("#Capitão");
console.log(regex);
console.log(regex.test("Aqui está o #Capitão"));
console.log(regex.test("Aqui está a Capita"));
console.log(regex.test("Aqui está o Capit"));
console.log(regex.test("Aqui está o Capital"));
