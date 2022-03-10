const body = document.body,
  cardDiv = body.querySelector("#card");
const addClickEventForButton = (i, func) => {
  const button = body.querySelector(`#buttons > .button:nth-child(${i})`);
  button.addEventListener("click", func);
};

// Expand
addClickEventForButton(1, () => (cardDiv.style.height = "46vh"));
// Reduce
addClickEventForButton(2, () => (cardDiv.style.height = "50px"));
// Close
addClickEventForButton(3, () => (body.style.display = "none"));

const rows = [
  "while (true) {",
  "const ideas = getIdeas();",
  "// difficult step coming...",
  "const chosenOne = chooseFromOne(ideas);",
  "",
  "writeHTMLAndCSS();",
  "writeJavaScript();",
  "const isOver = isItover(chosenOne);",
  "",
  "if (isOver)",
  "beProudOfYourCode();",
  "}"
];
const instructionsDiv = body.querySelector("#instructions");

const addWordsSpan = content => {
  const reWords = /[a-zA-Z]+/g;
  if (!reWords.test(content)) return document.createTextNode(content);

  const mainSpan = document.createElement("span");
  const space = content.match(/[ \/\\\(\)\{\};=]+/g);
  content.match(reWords).forEach((w, i) => {
    const span = document.createElement("span");
    span.className = /(^while)|(^if)/gi.test(w)
      ? "keyword"
      : /(^const)|(^let)/gi.test(w)
      ? "key-var"
      : /ideas|isOver|chosenOne/g.test(w)
      ? "variable"
      : /true/g.test(w)
      ? "true"
      : /[\/]{2}/.test(space.toString()) && /[a-zA-z+]/g.test(w)
      ? "comment"
      : "function";
    span.appendChild(document.createTextNode(w));
    if (space[i] == "// ") {
      mainSpan.appendChild(document.createTextNode(space[i] || ""));
      mainSpan.appendChild(span);
      mainSpan.appendChild(document.createTextNode(" "));
    } else {
      mainSpan.appendChild(span);
      mainSpan.appendChild(document.createTextNode(space[i] || ""));
    }
  });
  return mainSpan;
};
const generateSpan = (className, content) => {
  const span = document.createElement("span");
  span.className = className;
  span.appendChild(addWordsSpan(String(content)));
  return span;
};

rows.forEach((instruction, i) => {
  const indexSpan = generateSpan("index", i + 1);
  const instructionSpan = generateSpan("instruction", instruction);
  const rowDiv = document.createElement("div");
  rowDiv.className = `row ${
    i > 0 && i < 10 ? "indent1" : i === 10 ? "indent2" : ""
  }`;
  rowDiv.appendChild(indexSpan);
  rowDiv.appendChild(instructionSpan);
  instructionsDiv.appendChild(rowDiv);
});
