Feature: As a user, I can create a site

  Scenario: Navigate to the new site form
    Given user on the admin page
    And a "/home" draft page of type "blog:HomePage"
    When I click on the "Sites" link
    And I click on the "Add new site" button
    Then I see the text "New Site"
    Then I see the text "Create Site"

  Scenario: Create a site
    Given user on the admin page
    And a "/home" draft page of type "blog:HomePage"
    And a "/home/cat" draft page of type "blog:CategoryPage"
    And a "/home/dog" draft page of type "blog:CategoryPage"
    And a "/home/cat/my-first-article" draft page of type "blog:BlogPage"
    And a "/home/dog/the-second-one" draft page of type "blog:BlogPage"
    And a "/home/dog/the-third-one" draft page of type "blog:BlogPage"
    When I visit "/admin/sites/new"
    And I fill the field "hostname" with "www.example.net"
    And I fill the field "/index" with "/home"
    And I click on the "Create Site" button
    Then I see the text "www.example.net"
    And I see the text "/home"
