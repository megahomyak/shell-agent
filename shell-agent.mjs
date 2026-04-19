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
