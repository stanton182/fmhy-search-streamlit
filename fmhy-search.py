## Streamlit code
import streamlit as st
import requests
import base64
import re

# --- CONFIG ---
# Page and sidebar configuration
PAGE_TITLE = "FMHY Search"
PAGE_ICON_URL = "https://i.imgur.com/s9abZgP.png"
SIDEBAR_IMAGE_URL = "https://i.imgur.com/s9abZgP.png"
MENU_ITEMS = {
    'Get Help': 'https://github.com/Rust1667/fmhy-search-streamlit',
    'Report a bug': "https://github.com/Rust1667/fmhy-search-streamlit/issues",
    'About': "https://github.com/Rust1667/fmhy-search-streamlit"
}

# Sidebar links
SIDEBAR_LINKS = {
    "Wiki_Reddit": "https://www.reddit.com/r/FREEMEDIAHECKYEAH/wiki/index/",
    "Wiki_Net": "https://fmhy.net/",
    "Wiki_Pages": "https://fmhy.pages.dev/",
    "Wiki_TK": "https://www.fmhy.tk/",
    "Wiki_Vercel": "https://fmhy.vercel.app/",
    "Wiki_Raw_API": "https://api.fmhy.net/single-page",
    "Github_Web_App": "https://github.com/Rust1667/fmhy-search-streamlit",
    "Github_Script": "https://github.com/Rust1667/a-FMHY-search-engine",
    "Other_Search_Tools": "https://www.reddit.com/r/FREEMEDIAHECKYEAH/comments/105xraz/howto_search_fmhy/"
}

# Search behavior configuration
COLORING = False  # Many links won't work when this is active.
PRINT_RAW_MARKDOWN = False
FAILED_SEARCH_INFO_MSG = "For specific media or software, try a [CSE](https://fmhy.net/internet-tools#search-tools) / Live Sports [here](https://fmhy.net/videopiracyguide#live-tv-sports) / Ask in [Discord](https://www.reddit.com/r/FREEMEDIAHECKYEAH/comments/17f8msf/public_discord_server/)"
DO_ALT_INDEXING = True
DO_BASE64_DECODING = True
CACHE_TTL_SECONDS = 43200

# URLs and paths for data fetching
BASE64_RENTRY_URL = "https://rentry.co/FMHYBase64"
NSFWPIRACY_RENTRY_URL = "https://rentry.co/freemediafuckyeah/raw"
GITHUB_RAW_DOCS_URL_PREFIX = "https://raw.githubusercontent.com/fmhy/FMHYedit/main/docs/"
REDDIT_WIKI_URL_PREFIX = "https://www.reddit.com/r/FREEMEDIAHECKYEAH/wiki/"
PAGES_DEV_SITE_URL_PREFIX = "https://fmhy.net/"


# Wiki chunks configuration: (filename, icon, redditSubURL_or_absoluteURL)
WIKI_CHUNK_CONFIGS = [
    ("VideoPiracyGuide.md", "📺", "video"),
    ("AI.md", "🤖", "ai"),
    ("Android-iOSGuide.md", "📱", "android"),
    ("AudioPiracyGuide.md", "🎵", "audio"),
    ("DownloadPiracyGuide.md", "💾", "download"),
    ("EDUPiracyGuide.md", "🧠", "edu"),
    ("GamingPiracyGuide.md", "🎮", "games"),
    ("AdblockVPNGuide.md", "📛", "adblock-vpn-privacy"),
    ("System-Tools.md", "💻", "system-tools"),
    ("File-Tools.md", "🗃️", "file-tools"),
    ("Internet-Tools.md", "🔗", "internet-tools"),
    ("Social-Media-Tools.md", "💬", "social-media"),
    ("Text-Tools.md", "📝", "text-tools"),
    ("Video-Tools.md", "📼", "video-tools"),
    ("MISCGuide.md", "📂", "misc"),
    ("ReadingPiracyGuide.md", "📗", "reading"),
    ("TorrentPiracyGuide.md", "🌀", "torrent"),
    ("img-tools.md", "📷", "img-tools"),
    ("gaming-tools.md", "👾", "gaming-tools"),
    ("LinuxGuide.md", "🐧🍏", "linux"),
    ("DEVTools.md", "🖥️", "dev-tools"),
    ("Non-English.md", "🌏", "non-eng"),
    ("STORAGE.md", "🗄️", "storage")
    # ("base64.md", "🔑", BASE64_RENTRY_URL), # Special handling
    # ("NSFWPiracy.md", "🌶", NSFWPIRACY_RENTRY_URL) # Special handling
]
# --- END CONFIG ---

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON_URL,
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items=MENU_ITEMS
)


st.title(PAGE_TITLE)

with st.sidebar:
    st.image(SIDEBAR_IMAGE_URL, width=100)
    st.text("Search Engine for r/FREEMEDIAHECKYEAH")
    st.markdown("Links:")
    st.markdown(f"* Wiki: [Reddit]({SIDEBAR_LINKS['Wiki_Reddit']}), [.net]({SIDEBAR_LINKS['Wiki_Net']}) / [.pages]({SIDEBAR_LINKS['Wiki_Pages']}), [.tk]({SIDEBAR_LINKS['Wiki_TK']}) / [.vercel]({SIDEBAR_LINKS['Wiki_Vercel']}), [raw]({SIDEBAR_LINKS['Wiki_Raw_API']})")
    st.markdown(f"* [Github Repo (web-app)]({SIDEBAR_LINKS['Github_Web_App']})")
    st.markdown(f"* [Github Repo (script)]({SIDEBAR_LINKS['Github_Script']})")
    st.markdown(f"* [Other Search Tools for FMHY]({SIDEBAR_LINKS['Other_Search_Tools']})")

queryInputFromBox = st.text_input(label=" ", value="", help="Search for links in the Wiki.")


#----------------Alt Indexing------------
def addPretext(lines, icon, baseURL, subURL):
    """
    Processes a list of lines from a wiki page to prepend a formatted pretext to each content line.
    The pretext includes an icon, category/subcategory information derived from markdown headings,
    and a URL pointing to the relevant section of the wiki.

    Args:
        lines (list): A list of strings, where each string is a line from the wiki page.
        icon (str): An icon string to be included in the pretext.
        baseURL (str): The base URL of the wiki (e.g., "https://fmhy.net/").
        subURL (str): The specific sub-URL or page name (e.g., "videopiracyguide").

    Returns:
        list: A list of modified lines, with pretexts added to content lines.
    """
    modified_lines = []
    currMdSubheading = ""  # Stores the current markdown subheading anchor (e.g., "#some-subheading")
    currSubCat = ""        # Stores the current main category (e.g., "/ Video Streaming ")
    currSubSubCat = ""     # Stores the current sub-category (e.g., "/ Live TV Streaming ")

    for line in lines:
        # This block processes lines that start with "#", which are assumed to be markdown headings.
        # It updates currMdSubheading, currSubCat, and currSubSubCat based on the heading level and content.
        if line.startswith("#"): #Title Lines
            # Logic for most subURLs (not "storage")
            if not subURL=="storage":
                if line.startswith("# ►"):  # Main category heading (e.g., "# ► Video Streaming / Sites")
                    # Generates a URL-friendly anchor from the heading text.
                    currMdSubheading = "#" + line.replace("# ►", "").strip().replace(" / ", "-").replace(" ", "-").lower()
                    # Extracts the category name for display in the pretext.
                    currSubCat = "/ " + line.replace("# ►", "").strip() + " "
                    currSubSubCat = "" # Reset sub-subcategory
                elif line.startswith("## ▷"): # Sub-category heading (e.g., "## ▷ Live TV / Sports")
                    # Special handling for "non-english" subURL:
                    # Avoids overwriting currMdSubheading if it's the "non-english" page,
                    # because this section might have multiple sub-subcategories with the same name,
                    # and we want them to link to the broader "non-english" section anchor.
                    if not subURL=="non-english":
                        currMdSubheading = "#" + line.replace("## ▷", "").strip().replace(" / ", "-").replace(" ", "-").lower()
                    currSubSubCat = "/ " + line.replace("## ▷", "").strip() + " "
            # Logic specifically for the "storage" subURL, which uses different heading markers.
            elif subURL=="storage":
                if line.startswith("## "): # Main category for "storage" (e.g., "## Cloud Storage")
                    currMdSubheading = "#" + line.replace("## ", "").strip().replace(" / ", "-").replace(" ", "-").lower()
                    currSubCat = "/ " + line.replace("## ", "").strip() + " "
                    currSubSubCat = ""
                elif line.startswith("### "): # Sub-category for "storage" (e.g., "### File Hosting")
                    currMdSubheading = "#" + line.replace("### ", "").strip().replace(" / ", "-").replace(" ", "-").lower()
                    currSubSubCat = "/ " + line.replace("### ", "").strip() + " "

            # HTTP links are removed from category and sub-category titles.
            # This is done because including URLs directly in the pretext's display text
            # can mess up the markdown formatting and readability of the generated link.
            # The link is constructed separately in `preText`.
            if 'http' in currSubCat: currSubCat = '' # Note: This logic might need review if URLs in titles are desired
            if 'http' in currSubSubCat: currSubSubCat = '' # Note: This logic might need review if URLs in titles are desired

        # This block processes lines that are not headings but contain alphabetic characters (i.e., actual content).
        elif any(char.isalpha() for char in line): #If line has content
            # Constructs the pretext string.
            # It combines the icon, current category, and sub-category for display,
            # and forms a markdown link with baseURL, subURL, and the current subheading anchor.
            preText = f"[{icon}{currSubCat}{currSubSubCat}]({baseURL}{subURL}{currMdSubheading}) ► "
            # If the line starts with "* " (a common markdown list item marker),
            # it's stripped to avoid double list markers or awkward formatting.
            if line.startswith("* "): line = line[2:]
            modified_lines.append(preText + line)

    return modified_lines

#----------------base64 page processing------------

def fix_base64_string(encoded_string):
    missing_padding = len(encoded_string) % 4
    if missing_padding != 0:
        encoded_string += '=' * (4 - missing_padding)
    return encoded_string

def decode_base64_in_backticks(input_string):
    def base64_decode(match):
        encoded_data = match.group(0)[1:-1]  # Extract content within backticks
        decoded_bytes = base64.b64decode( fix_base64_string(encoded_data) )
        try:
            return decoded_bytes.decode()
        except:
            return encoded_data

    pattern = r"`[^`]+`"  # Regex pattern to find substrings within backticks
    decoded_string = re.sub(pattern, base64_decode, input_string)
    return decoded_string

def remove_empty_lines(text):
    lines = text.split('\n')  # Split the text into lines
    non_empty_lines = [line for line in lines if line.strip()]  # Filter out empty lines
    return '\n'.join(non_empty_lines)  # Join non-empty lines back together

def extract_base64_sections(base64_page):
    sections = base64_page.split("***")  # Split the input string by "***" to get sections
    formatted_sections = []
    for section in sections:
        formatted_section = remove_empty_lines( section.strip().replace("#### ", "").replace("\n\n", " - ").replace("\n", ", ") )
        if DO_BASE64_DECODING: formatted_section = decode_base64_in_backticks(formatted_section)
        formatted_section = f'[🔑Base64]({BASE64_RENTRY_URL}) ► ' + formatted_section
        formatted_sections.append(formatted_section)
    lines = formatted_sections
    return lines
#----------------</end>base64 page processing------------


def dlWikiChunk(fileName, icon, sub_url_or_absolute):

    #download the chunk
    page = ""
    try:
        if fileName == 'NSFWPiracy.md':
            print(f"Local file not found. Downloading {NSFWPIRACY_RENTRY_URL}...")
            response = requests.get(NSFWPIRACY_RENTRY_URL)
            response.raise_for_status() # Raise an exception for HTTP errors
            page = response.text.replace("\r", "")
        elif not fileName == 'base64.md':
            print("Downloading " + fileName + "...")
            url = GITHUB_RAW_DOCS_URL_PREFIX + fileName.lower()
            response = requests.get(url)
            response.raise_for_status()
            page = response.text
        elif fileName == 'base64.md':
            print(f"Downloading {BASE64_RENTRY_URL}/raw ...") # Corrected URL for raw content
            url = f"{BASE64_RENTRY_URL}/raw"
            response = requests.get(url)
            response.raise_for_status()
            page = response.text.replace("\r", "")
        print("Downloaded")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {fileName}: {e}. Skipping this file.")
        return []

    #add a pretext
    # redditBaseURL = REDDIT_WIKI_URL_PREFIX # Defined in CONFIG
    # pagesDevSiteBaseURL = PAGES_DEV_SITE_URL_PREFIX # Defined in CONFIG
    baseURL = PAGES_DEV_SITE_URL_PREFIX # Default base URL

    if not fileName == 'base64.md':
        # For regular files, sub_url_or_absolute is the subURL part
        pagesDevSiteSubURL = fileName.replace(".md", "").lower()
        # If sub_url_or_absolute is a full URL (like for NSFW piracy), use that as base
        if sub_url_or_absolute.startswith("http"):
             baseURL = "" # The sub_url_or_absolute is the full URL here
             subURL = sub_url_or_absolute
        else:
            subURL = pagesDevSiteSubURL # Standard case based on filename
        
        lines = page.split('\n')
        # Determine actual base URL for pretext
        # If using reddit links for pretext:
        # current_base_url_for_pretext = REDDIT_WIKI_URL_PREFIX
        # If using pages.dev links for pretext:
        current_base_url_for_pretext = PAGES_DEV_SITE_URL_PREFIX

        lines = addPretext(lines, icon, current_base_url_for_pretext, subURL)
    elif fileName == 'base64.md':
        lines = extract_base64_sections(page)

    return lines

def cleanLineForSearchMatchChecks(line):
    # Normalize URLs for consistent search matching
    return line.replace(REDDIT_WIKI_URL_PREFIX, '/').replace(PAGES_DEV_SITE_URL_PREFIX, '/')

@st.cache_resource(ttl=CACHE_TTL_SECONDS)
def alternativeWikiIndexing():
    wikiChunks = []
    for config_tuple in WIKI_CHUNK_CONFIGS:
        fileName, icon, sub_url = config_tuple
        wikiChunks.append(dlWikiChunk(fileName, icon, sub_url))
    
    # Manually add special cased files if needed, or integrate them into WIKI_CHUNK_CONFIGS with a flag
    # For example, if base64.md and NSFWPiracy.md need to be included:
    wikiChunks.append(dlWikiChunk("base64.md", "🔑", BASE64_RENTRY_URL)) # The sub_url is not used in current dlWikiChunk for base64
    wikiChunks.append(dlWikiChunk("NSFWPiracy.md", "🌶", "https://saidit.net/s/freemediafuckyeah/wiki/index")) # Example of using a full URL

    return [item for sublist in wikiChunks for item in sublist] #Flatten a <list of lists of strings> into a <list of strings>
#--------------------------------

def getAllLines():
    #if DO_ALT_INDEXING: # Check the flag from CONFIG
    return alternativeWikiIndexing()

def removeEmptyStringsFromList(stringList):
    return [string for string in stringList if string != '']

def checkMultiWordQueryContainedExactlyInLine(line, searchQuery):
    if len(searchQuery.split(' ')) <= 1:
        return False
    return (searchQuery.lower() in line.lower())

def moveExactMatchesToFront(myList, searchQuery):
    bumped = []
    notBumped = []
    for i in range(len(myList)):
        if checkMultiWordQueryContainedExactlyInLine(myList[i], searchQuery):
            bumped.append(myList[i])
        else:
            notBumped.append(myList[i])
    return (bumped + notBumped)

def checkList1isInList2(list1, list2):
    for element in list1:
        if element not in list2:
            return False
    return True

def checkWordForWordMatch(line, searchQuery):
    lineWords = removeEmptyStringsFromList( line.lower().replace('[', ' ').replace(']', ' ').split(' ') )
    # Necessary in Streamlit: .strip() ensures accurate word matching.
    # This is likely due to the way strings are processed or passed in the Streamlit environment,
    # potentially leaving leading/trailing whitespace on words after split(), which would cause matching to fail.
    lineWords = [element.strip() for element in lineWords]
    searchQueryWords = removeEmptyStringsFromList( searchQuery.lower().split(' ') )
    return checkList1isInList2(searchQueryWords, lineWords)

def moveBetterMatchesToFront(myList, searchQuery):
    bumped = []
    notBumped = []
    for element in myList:
        if checkWordForWordMatch(element, searchQuery):
            bumped.append(element)
        else:
            notBumped.append(element)
    return (bumped + notBumped)

def getOnlyFullWordMatches(myList, searchQuery):
    bumped = []
    for element in myList:
        if checkWordForWordMatch(element, searchQuery):
            bumped.append(element)
    return bumped

def getLinesThatContainAllWords(lineList, searchQuery):
    words = removeEmptyStringsFromList( searchQuery.lower().split(' ') )
    bumped = []
    for line in lineList:
        if DO_ALT_INDEXING: # Check the flag from CONFIG
            lineModdedForChecking = cleanLineForSearchMatchChecks(line).lower()
        else:
            lineModdedForChecking = line.lower()
        for word in words:
            if word not in lineModdedForChecking:
                break
        else:
            bumped.append(line)
    return bumped

def filterLines(lineList, searchQuery):
    if len(searchQuery)<=2 or (searchQuery==searchQuery.upper() and len(searchQuery)<=5):
        return getOnlyFullWordMatches(lineList, searchQuery)
    else:
        return getLinesThatContainAllWords(lineList, searchQuery)

def filterOutTitleLines(lineList):
    filteredList = []
    sectionTitleList = []
    for line in lineList:
        if line[0] != "#":
            filteredList.append(line)
        else:
            sectionTitleList.append(line)
    return [filteredList, sectionTitleList]



def doASearch(searchInput):
    searchInput = searchInput.strip()

    #make sure the input is right before continuing
    if searchInput=="":
        st.warning("The search query is empty.", icon="⚠️")
        return
    #if len(searchInput)<2 and not searchInput=="⭐":
    #    st.warning("The search query is too short.", icon="⚠️")
    #    return

    #main results
    myLineList = lineList
    linesFoundPrev = filterLines(myLineList, searchInput)

    #show only full word matches if there are too many results
    if len(linesFoundPrev) > 300:
        toomanywarningmsg = "Too many results (" + str(len(linesFoundPrev)) + "). " + "Showing only full-word matches."
        st.text(toomanywarningmsg)
        linesFoundPrev = getOnlyFullWordMatches(linesFoundPrev, searchInput)

    #rank results
    #linesFoundPrev = moveExactMatchesToFront(linesFoundPrev, searchInput)
    linesFoundPrev = moveBetterMatchesToFront(linesFoundPrev, searchInput)

    #extract titles lines
    linesFoundAll = filterOutTitleLines(linesFoundPrev)
    linesFound = linesFoundAll[0]
    sectionTitleList = linesFoundAll[1]

    #make sure results are not too many before continuing
    if len(linesFound) > 700 and not searchInput=="⭐":
        toomanywarningmsg = "Too many results (" + str(len(linesFound)) + ")."
        st.warning(toomanywarningmsg, icon="⚠️")

        #Print the section titles
        if len(sectionTitleList)>0:
            st.markdown(" ")
            st.markdown("There are these section titles in the Wiki: ")
            sectionTitleListToPrint = "\n\n".join(sectionTitleList)
            st.code(sectionTitleListToPrint, language="markdown")
            #st.markdown(" ")
            st.markdown("Find them by doing <Ctrl+F> in the [Raw markdown](https://api.fmhy.net/single-page).")

        return

    myFilterWords = searchInput.lower().split(' ')

    #create string of text to print
    textToPrint = "\n\n".join(linesFound)

    #print search results count
    if len(linesFound)>0:
        st.text(str(len(linesFound)) + " search results for " + searchInput + ":\n")
    else:
        st.markdown("No results found for " + searchInput + "!")
        st.info(failedSearchInfoMsg, icon="ℹ️")

    # print search results
    if not PRINT_RAW_MARKDOWN: # Check the flag from CONFIG
        st.markdown(textToPrint)
    else:
        st.code(textToPrint, language="markdown")

    #title section results
    if len(sectionTitleList)>0:
        st.markdown(" ")
        st.markdown("Also there are these section titles in the Wiki: ")
        sectionTitleListToPrint = "\n\n".join(sectionTitleList)
        st.code(sectionTitleListToPrint, language="markdown")
        #st.markdown(" ")
        st.markdown(f"Find them by doing <Ctrl+F> in the [Raw markdown]({SIDEBAR_LINKS['Wiki_Raw_API']}).") # Use constant

    #Some results but maybe not enough
    if len(linesFound)>0 and len(linesFound)<=10:
        with st.expander("Not what you were looking for?"):
            st.info(FAILED_SEARCH_INFO_MSG, icon="ℹ️") # Use constant


## Execute at start of script
# Global variable `lineList` initialized here.
# Ensure functions using it are defined above or it's passed as an argument.
lineList = getAllLines()


if st.button("Search"):
    queryInput = queryInputFromBox
    doASearch(queryInput)
