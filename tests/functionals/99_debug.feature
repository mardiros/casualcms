Feature: As a developper, I want a browser open with a session

  @dev
  Scenario: start an initialized session and wait
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
    And a "contact" setting on site "localhost"
    And publish the "/home" page on "localhost:6556"
    When I visit "/admin/pages?parent=/home"
    When I visit "/"
    And I wait
