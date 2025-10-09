const links = [];
async function getLinks(url) {
  try {
    const response = await fetch(url, {
      method: "GET",
    });

    console.log("received response");
    // Check if the request was successful (status code 200-299)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const html = await response.text();
    if (html) {
      console.log("HTML structure received:");
      console.log("waiting for all html to load in...");
      await new Promise((resolve) => setTimeout(resolve, 2500)); // wait for 2.5 seconds
      // You can now parse or manipulate this HTML string
      // For example, to create a DOM object:
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, "text/html");
      console.log("Parsed DOM");
      tableBodies = doc.getElementsByTagName("tbody");
      if (tableBodies.length !== 4) {
        throw new Error("Expected 4 table bodies, found " + tableBodies.length);
      } else {
        console.log("Found 4 table bodies");
      }
      tableBody = tableBodies[3];
      console.log("table body: ");
      console.log(tableBody);
      console.log(tableBody.children);
      for (let child of tableBody.children) {
        id = child.children[0].innerText;
        url = `https://poker.rchase.com/hand/${id}/history`;
        links.push(url);
        console.log("Found link: " + url);
      }
    } else {
      console.log("Failed to retrieve HTML.");
    }

    console.log("setting local storage");
    localStorage.setItem("links", JSON.stringify(links));
  } catch (error) {
    console.error("Error fetching HTML:", error);
    return null;
  }
}

async function getHand(url) {
  try {
    const response = await fetch(url, {
      method: "GET",
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const html = await response.text();
    if (html) {
      firstBracket = html.indexOf("[");
      lastBracket = html.indexOf("]");
      return html.substring(firstBracket + 1, lastBracket);
    } else {
      console.log("Failed to retrieve HTML.");
      throw new Error("Failed to retrieve HTML.");
    }
  } catch (error) {
    console.error("Error fetching hand:", error);
    return "error";
  }
}

function displayLinks(links) {
  for (const link of links) {
    console.log("getting hand for: " + link);
    const p = document.createElement("p");
    p.classList.add("hand");
    getHand(link).then((hand) => {
      console.log(`Hand for ${link}: ${hand}`);
      p.innerText = hand;
    });
    document.querySelector(".data").appendChild(p);
  }
  console.log("all hands displayed");
}

async function grabAllLinks(targetUrl) {
  for (let i = 0; i < 13; i++) {
    console.log("getting html of page " + (i + 1));
    pageUrl = targetUrl + "?page=" + (i + 1);
    await getLinks(targetUrl);
    console.log("done with page " + (i + 1));
  }
  console.log("all links collected");
  displayLinks(links);
}

const targetUrl = "https://poker.rchase.com/";
linksList = JSON.parse(localStorage.getItem("links"));
if (linksList && linksList.length !== 0) {
  console.log("getting links from local storage");
  linksList = JSON.parse(localStorage.getItem("links"));
  displayLinks(linksList);
} else {
  grabAllLinks(targetUrl);
}
