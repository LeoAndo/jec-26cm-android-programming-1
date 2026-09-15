package jp.ac.jec.a04webviewapp;

/**
 * MenuやMenuItemだと、android.view.Menuやandroid.view.MenuItemと被るためAppMenuItemとして定義した
 */
enum AppMenuItem {
    YAHOO("https://news.yahoo.co.jp/", "Yahoo!ニュース"),
    GITHUB_COPILOT("https://github.com/features/copilot/", "GitHub Copilot"),
    SLAM_DUNK_MOVIE("https://slamdunk-movie.jp/", "映画「SLAM DUNK」公式サイト"),
    CHAT_GPT("https://openai.com/ja-JP/chatgpt/overview/", "OpenAI ChatGPT");

    private final String url;
    private final String title;

    AppMenuItem(String url, String title) {
        this.url = url;
        this.title = title;
    }

    String getUrl() {
        return url;
    }

    String getTitle() {
        return title;
    }
}