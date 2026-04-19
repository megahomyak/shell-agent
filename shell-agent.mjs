import * as process from "node:process";
import * as groq from "groq-sdk";
import * as fs from "node:fs";

let runPass = async (startingPrompt, complete, execute, history) => {
    let completion = "";
    process.stdout.write("$ ");
    for await (let part of complete(startingPrompt, history)) {
        process.stdout.write(part.replace("\n", "$ \n"));
        completion += part;
    }
    process.stdout.write("\n");
    let execution = "";
    process.stdout.write("< ");
    for await (let part of execute(completion)) {
        process.stdout.write(part.replace("\n", "< \n"));
        execution += part;
    }
    process.stdout.write("\n");
    return { completion, execution };
};

let runLoop = async (startingPrompt, complete, execute, history) => {
    while (true) {
        runPass(startingPrompt, complete, execute, history);
    }
};

{
    let groq = new groq.Groq();
    let startingPrompt = fs.readFileSync("starting_prompt.txt", "utf-8");
    let complete = async (groq, history) => {
        return groq.chat.completions.create({
            model: "llama-3.3-70b-versatile",
            messages: history,
            stream: true,
        });
    };
    let execute 
    runLoop(startingPrompt, complete, execute, history)
}
