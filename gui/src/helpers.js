

async function post(url = '', data = {}){
    const options = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'mode': 'no-cors'
        },
        body: JSON.stringify(data)
    }

    await fetch(url, options).catch((error) => {console.error('Error:', error)});
}


function get(url = ''){
    const options = {
        method: 'GET',
        headers: new Headers()
    }

    const data = fetch(url, options)
    .catch((error) => {console.error('Error:', error)})
    .then((response) => {
        return response.json();
    });

    return JSON.parse(data);
}

export {post, get};


