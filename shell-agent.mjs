import * as process from "node:process";

let runPass = async (startingPrompt, complete, execute, history) => {
    let completion = "";
    for await (let part of complete(startingPrompt, history)) {
        process.stdout.write(part);
        completion += part;
    }
    let execution = "";
    for await (let part of execute(completion)) {
        process.stdout.write(part);
        execution += part;
    }
    return { completion, execution };
};

let parseHistory = (history) => {
    let history = [];
    for (let block of history.split("\n\n")) {
        if (!block) continue;
        let role = block[0] == "$" ? "assistant" : "user";
        let contentLines = [];
        for (let line in block.split("\n")) {
            contentLines.push(line.substring(2));
        }
        let content = contentLines.join("\n");
        history.push({ role, content });
    }
    return history;
};
