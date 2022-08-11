Feature: As a user, I can create a site

  Scenario: Navigate to the new site form
    Given user on the admin page
    And a "/home" page of type "blog:HomePage"
    When I click on the "Sites" link
    And I click on the "Add new site" button
    Then I see the text "New Site"
    Then I see the text "Submit"

  Scenario: Create a site
    Given user on the admin page
    And a "/home" page of type "blog:HomePage"
    And a "/home/cat" page of type "blog:CategoryPage"
    And a "/home/dog" page of type "blog:CategoryPage"
    And a "/home/cat/my-first-article" page of type "blog:BlogPage"
    And a "/home/dog/the-second-one" page of type "blog:BlogPage"
    And a "/home/dog/the-third-one" page of type "blog:BlogPage"
    When I visit "/admin/site/new"
    And I fill the field "hostname" with "www.example.net"
    And I fill the field "/index" with "/home"
    And I click on the "Submit" button
    Then I see the text "www.example.net"
    And I see the text "/home"


  Scenario: Display site path
    Given user on the admin page
    And a "/home" page of type "blog:HomePage"
    And a "/home/cat" page of type "blog:CategoryPage"
    And a "/home/dog" page of type "blog:CategoryPage"
    And a "/home/cat/my-first-article" page of type "blog:BlogPage"
    And a "127.0.0.1:6556" site with "/home/cat" root page
    When I visit "http://127.0.0.1:6556/"
    Then I see the text "Cat"
    When I visit "http://127.0.0.1:6556/my-first-article"
    Then I see the text "My First Article"
