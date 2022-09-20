Feature: As a user, I want to publish a web page

  Scenario: Create and publish a page, then visit it
    Given user on the admin page
    And a "/home" draft page of type "blog:HomePage"
    And a "/home/cat" draft page of type "blog:CategoryPage"
    And a "/home/dog" draft page of type "blog:CategoryPage"
    And a "/home/cat/my-first-article" draft page of type "blog:BlogPage"
    And a "/home/dog/the-second-one" draft page of type "blog:BlogPage"
    And a "/home/dog/the-third-one" draft page of type "blog:BlogPage"
    And a "header" snippet of type "blog:HeaderSnippet"
    And a "127.0.0.1:6556" site with "/home" root page
    And a "localhost:6556" site with "/home" root page
    And a "contact" setting on site "localhost:6556"
    When I visit "/admin/pages/edit?page=%2Fhome"
    And I click on the "Publish" button
    And I click on the "localhost:6556" label
    And I click on the "Submit" button having the role "publish"
    And I click on the "View" link ignoring the target attribute
    Then I see the text "welcome home bro!"

  Scenario: Create and publish a page, then visit it
    Given user on the admin page
    And a "/home" draft page of type "blog:HomePage"
    And a "/home/cat" draft page of type "blog:CategoryPage"
    And a "/home/dog" draft page of type "blog:CategoryPage"
    And a "/home/cat/my-first-article" draft page of type "blog:BlogPage"
    And a "/home/dog/the-second-one" draft page of type "blog:BlogPage"
    And a "/home/dog/the-third-one" draft page of type "blog:BlogPage"
    And a "header" snippet of type "blog:HeaderSnippet"
    And a "127.0.0.1:6556" site with "/home" root page
    And a "localhost:6556" site with "/home" root page
    And a "contact" setting on site "localhost:6556"
    And publish the "/home" page on "localhost:6556"
    When I visit "/"
    Then I see the text "welcome home bro!"
