let run = async (initialPrompt, history, aiComplete, shellInvoke) => {
    for (;;) {
        let aiCompletion = await aiComplete(initialPrompt, history.getter);
        console.log("$" + aiCompletion.replace("\n", "\n$ ") + "\n");
        let shellInvocation = await shellInvoke(aiCompletion);
        console.log("<" + aiCompletion.replace("\n", "\n< ") + "\n");
        history.push({
            aiCompletion,
            shellInvocation,
        });
    }
};

{

}
